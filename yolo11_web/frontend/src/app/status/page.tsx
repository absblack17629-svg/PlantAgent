"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { RefreshCw, Activity, Database, Cpu, HardDrive, AlertCircle } from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface SystemMetrics {
  cpu: { percent: number; count: number };
  memory: { percent: number; used_gb: number; total_gb: number };
  disk: { percent: number; used_gb: number; total_gb: number };
  timestamp: string;
}

interface HealthStatus {
  overall_status: string;
  components: {
    [key: string]: {
      status: string;
      message?: string;
    };
  };
}

interface Alert {
  rule_name: string;
  level: string;
  message: string;
  triggered_at: string;
}

export default function StatusPage() {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // 获取系统指标
      const metricsRes = await fetch(`${API_URL}/api/monitoring/metrics/current`);
      if (metricsRes.ok) {
        const data = await metricsRes.json();
        setMetrics(data);
      }

      // 获取健康状态
      const healthRes = await fetch(`${API_URL}/api/monitoring/health`);
      if (healthRes.ok) {
        const data = await healthRes.json();
        setHealth(data);
      }

      // 获取活跃告警
      const alertsRes = await fetch(`${API_URL}/api/monitoring/alerts/active`);
      if (alertsRes.ok) {
        const data = await alertsRes.json();
        setAlerts(data.alerts || []);
      }
    } catch (err) {
      console.error("获取系统状态失败:", err);
      setError("无法连接到后端服务");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // 每5秒刷新
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "healthy":
      case "ok":
        return "text-green-600 bg-green-50";
      case "degraded":
      case "warning":
        return "text-yellow-600 bg-yellow-50";
      case "unhealthy":
      case "error":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getAlertColor = (level: string) => {
    switch (level.toUpperCase()) {
      case "CRITICAL":
        return "border-red-500 bg-red-50";
      case "ERROR":
        return "border-orange-500 bg-orange-50";
      case "WARNING":
        return "border-yellow-500 bg-yellow-50";
      default:
        return "border-blue-500 bg-blue-50";
    }
  };

  if (loading && !metrics) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* 页面标题 */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">系统状态</h1>
            <p className="text-gray-600">实时监控系统运行状态和性能指标</p>
          </div>
          <Button onClick={fetchData} variant="outline" size="sm">
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? "animate-spin" : ""}`} />
            刷新
          </Button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* 整体健康状态 */}
        {health && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                整体状态
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`inline-flex items-center px-4 py-2 rounded-full text-lg font-semibold ${getStatusColor(health.overall_status)}`}>
                {health.overall_status === "healthy" ? "✓ 正常运行" : "⚠ 需要关注"}
              </div>

              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(health.components).map(([name, component]) => (
                  <div key={name} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{name}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getStatusColor(component.status)}`}>
                        {component.status}
                      </span>
                    </div>
                    {component.message && (
                      <p className="text-sm text-gray-600 mt-1">{component.message}</p>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 系统指标 */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* CPU */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Cpu className="h-4 w-4" />
                  CPU 使用率
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold mb-2">{metrics.cpu.percent.toFixed(1)}%</div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      metrics.cpu.percent > 80 ? "bg-red-500" : metrics.cpu.percent > 60 ? "bg-yellow-500" : "bg-green-500"
                    }`}
                    style={{ width: `${metrics.cpu.percent}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-2">{metrics.cpu.count} 核心</p>
              </CardContent>
            </Card>

            {/* 内存 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Database className="h-4 w-4" />
                  内存使用率
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold mb-2">{metrics.memory.percent.toFixed(1)}%</div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      metrics.memory.percent > 85 ? "bg-red-500" : metrics.memory.percent > 70 ? "bg-yellow-500" : "bg-green-500"
                    }`}
                    style={{ width: `${metrics.memory.percent}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {metrics.memory.used_gb.toFixed(1)} / {metrics.memory.total_gb.toFixed(1)} GB
                </p>
              </CardContent>
            </Card>

            {/* 磁盘 */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <HardDrive className="h-4 w-4" />
                  磁盘使用率
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold mb-2">{metrics.disk.percent.toFixed(1)}%</div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      metrics.disk.percent > 85 ? "bg-red-500" : metrics.disk.percent > 70 ? "bg-yellow-500" : "bg-green-500"
                    }`}
                    style={{ width: `${metrics.disk.percent}%` }}
                  />
                </div>
                <p className="text-sm text-gray-600 mt-2">
                  {metrics.disk.used_gb.toFixed(1)} / {metrics.disk.total_gb.toFixed(1)} GB
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* 活跃告警 */}
        {alerts.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-red-500" />
                活跃告警 ({alerts.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {alerts.map((alert, index) => (
                  <div key={index} className={`p-4 border-l-4 rounded ${getAlertColor(alert.level)}`}>
                    <div className="flex items-start justify-between">
                      <div>
                        <div className="font-semibold">{alert.rule_name}</div>
                        <div className="text-sm text-gray-700 mt-1">{alert.message}</div>
                        <div className="text-xs text-gray-500 mt-2">
                          {new Date(alert.triggered_at).toLocaleString("zh-CN")}
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-1 rounded font-semibold ${getAlertColor(alert.level)}`}>
                        {alert.level}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 最后更新时间 */}
        {metrics && (
          <div className="mt-6 text-center text-sm text-gray-500">
            最后更新: {new Date(metrics.timestamp).toLocaleString("zh-CN")}
          </div>
        )}
      </div>
    </div>
  );
}
