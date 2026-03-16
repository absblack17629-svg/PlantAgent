"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { History, RefreshCw, AlertCircle, CheckCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface HistoryItem {
  id: number;
  user_id: number;
  action_type: string;
  item_id?: number;
  item_title?: string;
  action_detail?: string;
  created_at: string;
}

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  // 从父窗口获取 token
  useEffect(() => {
    const getTokenFromParent = () => {
      // 检查是否在 iframe 中
      const isInIframe = window.self !== window.top;
      
      if (isInIframe) {
        console.log('在 iframe 中，向父窗口请求 token');
        
        // 监听来自父窗口的消息
        const handleMessage = (event: MessageEvent) => {
          if (event.origin !== window.location.origin) {
            return;
          }

          if (event.data.type === 'TOKEN_RESPONSE') {
            console.log('收到父窗口的 token:', !!event.data.token);
            setToken(event.data.token);
          }
        };

        window.addEventListener('message', handleMessage);

        // 向父窗口请求 token
        window.parent.postMessage({ type: 'REQUEST_TOKEN' }, window.location.origin);

        return () => window.removeEventListener('message', handleMessage);
      } else {
        // 不在 iframe 中，直接从 localStorage 获取
        console.log('不在 iframe 中，从 localStorage 获取 token');
        const localToken = localStorage.getItem('token');
        setToken(localToken);
      }
    };

    getTokenFromParent();
  }, []);

  // 当 token 可用时获取历史记录
  useEffect(() => {
    if (token !== null) {
      fetchHistory(token);
    }
  }, [token]);

  const fetchHistory = async (authToken: string | null) => {
    try {
      setLoading(true);
      
      console.log("开始获取历史记录, token 存在:", !!authToken);
      
      if (!authToken) {
        setIsLoggedIn(false);
        setError("请先登录后再查看检测历史");
        setLoading(false);
        return;
      }

      setIsLoggedIn(true);
      
      const response = await fetch(`${API_URL}/api/history?skip=0&limit=50`, {
        headers: { 
          Authorization: `Bearer ${authToken}`,
          "Content-Type": "application/json"
        },
      });

      console.log("API 响应状态:", response.status);

      if (response.status === 401 || response.status === 403) {
        setError("登录已过期，请重新登录");
        if (typeof window !== 'undefined') {
          localStorage.removeItem("token");
        }
        return;
      }
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("API 错误响应:", errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      console.log("历史记录数据:", data);
      console.log("数据类型:", Array.isArray(data) ? "数组" : typeof data);
      console.log("数据长度:", Array.isArray(data) ? data.length : "N/A");
      
      // 只显示检测历史
      const detectionHistory = (data || []).filter((item: any) => item.action_type === 'detection');
      console.log("检测历史数量:", detectionHistory.length);
      setHistory(detectionHistory);
      setError(null);
    } catch (err) {
      console.error("获取检测历史失败:", err);
      setError(err instanceof Error ? err.message : "获取检测历史失败");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (actionType: string) => {
    switch (actionType?.toLowerCase()) {
      case "detection": return "text-green-600 bg-green-50";
      case "view_news": return "text-blue-600 bg-blue-50";
      case "search": return "text-purple-600 bg-purple-50";
      default: return "text-gray-600 bg-gray-50";
    }
  };

  const getActionTypeLabel = (actionType: string) => {
    switch (actionType?.toLowerCase()) {
      case "detection": return "病害检测";
      case "view_news": return "浏览资讯";
      case "search": return "搜索查询";
      default: return "其他操作";
    }
  };

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleString("zh-CN");
    } catch {
      return dateStr;
    }
  };

  return (
    <div className="container mx-auto py-4 px-3 sm:py-8 sm:px-4">
      <div className="max-w-4xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-6 sm:mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
            检测历史
          </h1>
          <p className="text-sm sm:text-base text-gray-600">
            查看您的病害检测记录
          </p>
        </div>

        {loading ? (
          <Card>
            <CardContent className="py-12 text-center">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto text-gray-400" />
              <p className="mt-4 text-gray-500">加载中...</p>
            </CardContent>
          </Card>
        ) : error ? (
          <Card>
            <CardContent className="py-8 text-center">
              <AlertCircle className="h-12 w-12 mx-auto text-yellow-500 mb-4" />
              <p className="text-gray-600 mb-4">{error}</p>
              {!isLoggedIn && (
                <Button onClick={() => window.location.href = "/?page=login"}>
                  去登录
                </Button>
              )}
            </CardContent>
          </Card>
        ) : history.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <History className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">暂无检测记录</p>
              <Button 
                variant="outline" 
                className="mt-4"
                onClick={() => window.location.href = "/?page=detect"}
              >
                去做检测
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {history.map((item) => (
              <Card key={item.id} className="overflow-hidden">
                <CardContent className="p-4">
                  <div className="flex flex-col sm:flex-row gap-4">
                    {/* 图片 */}
                    <div className="w-full sm:w-24 h-24 flex-shrink-0 bg-gray-100 rounded-lg overflow-hidden">
                      {item.action_detail && (item.action_detail.startsWith('http') || item.action_detail.startsWith('/static')) ? (
                        <img 
                          src={item.action_detail.startsWith('http') ? item.action_detail : `${API_URL}${item.action_detail}`}
                          alt="检测图片"
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.parentElement!.innerHTML = '<div class="w-full h-full flex items-center justify-center text-gray-400"><svg class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg></div>';
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          <History className="h-8 w-8" />
                        </div>
                      )}
                    </div>
                    
                    {/* 信息 */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">
                            {item.item_title || "病害检测记录"}
                          </h3>
                          <p className="text-sm text-gray-500 mt-1">
                            {formatDate(item.created_at)}
                          </p>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(item.action_type)}`}>
                          {getActionTypeLabel(item.action_type)}
                        </span>
                      </div>
                      
                      {item.action_detail && !item.action_detail.startsWith('http') && !item.action_detail.startsWith('/static') && (
                        <div className="mt-2 text-sm text-gray-600 line-clamp-2">
                          {item.action_detail}
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
