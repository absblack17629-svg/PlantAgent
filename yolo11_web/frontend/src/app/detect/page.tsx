// -*- coding: utf-8 -*-
/**
 * 病害检测页面
 * 上传图片 -> 检测 -> 查看结果
 */

"use client";

import { useState, useCallback } from "react";
import { ImageUpload } from "@/components/disease-detection/ImageUpload";
import { DetectionVisualizer } from "@/components/disease-detection/DetectionVisualizer";
import { DetectionResultCard } from "@/components/disease-detection/DetectionResultCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Loader2, Send, History } from "lucide-react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DetectionResult {
  success: boolean;
  disease_found: boolean;
  disease_type: string;
  confidence: number;
  severity: string;
  detections: any[];
  prevention_scheme?: string;
  image_url: string;
  detection_time: string;
  duration_ms: number;
  model_version: string;
}

export default function DetectionPage() {
  const router = useRouter();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleImageSelect = useCallback((file: File, preview: string) => {
    setSelectedFile(file);
    setPreviewUrl(preview);
    setResult(null);
    setError(null);
  }, []);

  const handleDetect = async () => {
    if (!selectedFile) return;

    setIsLoading(true);
    setError(null);

    try {
      // 创建FormData
      const formData = new FormData();
      formData.append("file", selectedFile);

      // 调用真正的病害检测API
      // 注意：API路径是 /api/detection/upload
      const response = await fetch('http://localhost:8000/api/detection/upload', {
        method: 'POST',
        body: formData,
        // 不设置credentials避免CORS问题
        mode: 'cors',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`检测失败: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error("检测错误:", err);
      setError(err instanceof Error ? err.message : "检测过程中发生错误");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            水稻病害检测
          </h1>
          <p className="text-gray-600">
            上传水稻叶片图片，AI智能识别病害类型并提供防治方案
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 左侧: 图片上传和可视化 */}
          <div className="space-y-6">
            {/* 上传区域 */}
            <Card>
              <CardHeader>
                <CardTitle>1. 上传图片</CardTitle>
              </CardHeader>
              <CardContent>
                <ImageUpload
                  onImageSelect={handleImageSelect}
                  accept="image/png,image/jpeg,image/jpg,image/webp"
                  maxSize={10 * 1024 * 1024}
                />

                {/* 操作按钮 */}
                <div className="mt-4 flex gap-3">
                  <Button
                    onClick={handleDetect}
                    disabled={!selectedFile || isLoading}
                    className="flex-1"
                  >
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        检测中...
                      </>
                    ) : (
                      <>
                        <Send className="mr-2 h-4 w-4" />
                        开始检测
                      </>
                    )}
                  </Button>

                  {result && (
                    <Button variant="outline" onClick={handleReset}>
                      重新检测
                    </Button>
                  )}
                </div>

                {/* 错误提示 */}
                {error && (
                  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-sm text-red-600">{error}</p>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* 检测结果可视化 */}
            {result && previewUrl && (
              <DetectionVisualizer
                imageUrl={previewUrl}
                detections={result.detections}
                showLabels={true}
                showConfidence={true}
              />
            )}
          </div>

          {/* 右侧: 检测结果 */}
          <div className="space-y-6">
            {result ? (
              <DetectionResultCard result={result} />
            ) : (
              <Card className="h-full flex items-center justify-center min-h-[400px]">
                <div className="text-center text-gray-400">
                  <div className="mb-4">
                    <svg
                      className="mx-auto h-16 w-16"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1}
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                  <p>上传图片并开始检测</p>
                  <p className="text-sm mt-2">检测结果将显示在这里</p>
                </div>
              </Card>
            )}

            {/* 历史记录入口 */}
            <Card>
              <CardContent className="pt-6">
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => router.push("/user/history")}
                >
                  <History className="mr-2 h-4 w-4" />
                  查看检测历史
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
