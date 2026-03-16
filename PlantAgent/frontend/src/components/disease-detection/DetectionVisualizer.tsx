// -*- coding: utf-8 -*-
/**
 * 病害检测可视化组件
 * 在图像上标注病斑边界框和检测结果
 */

"use client";

import { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface Detection {
  class: string;
  disease_type: string;
  disease_name: string;
  confidence: number;
  bbox: number[]; // [x1, y1, x2, y2]
  severity: string;
  description?: string;
}

interface DetectionVisualizerProps {
  imageUrl: string;
  detections: Detection[];
  showLabels?: boolean;
  showConfidence?: boolean;
  className?: string;
}

// 病害类型颜色映射
const diseaseColors: Record<string, string> = {
  白叶枯病: "#FF6B6B",    // 红色
  稻瘟病: "#FFA500",       // 橙色
  褐斑病: "#4ECDC4",       // 青色
  健康: "#95E1D3",          // 浅绿
  默认: "#888888",
};

// 严重程度颜色
const severityColors: Record<string, string> = {
  mild: "#4CAF50",      // 绿色
  moderate: "#FF9800",  // 橙色
  severe: "#F44336",   // 红色
};

export function DetectionVisualizer({
  imageUrl,
  detections,
  showLabels = true,
  showConfidence = true,
  className = "",
}: DetectionVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [imageSize, setImageSize] = useState({ width: 0, height: 0 });
  const [imageLoaded, setImageLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement | null>(null);

  // 加载图像
  useEffect(() => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      imgRef.current = img;
      setImageSize({ width: img.width, height: img.height });
      setImageLoaded(true);
    };
    img.onerror = () => {
      console.error("Failed to load image:", imageUrl);
    };
    img.src = imageUrl;
  }, [imageUrl]);

  // 绘制边界框
  useEffect(() => {
    if (!canvasRef.current || !imageLoaded || !imgRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // 设置画布大小与图像一致
    canvas.width = imageSize.width;
    canvas.height = imageSize.height;

    // 绘制图像
    ctx.drawImage(imgRef.current, 0, 0);

    // 绘制边界框
    detections.forEach((detection, index) => {
      const { bbox, disease_type, confidence, severity } = detection;
      if (!bbox || bbox.length < 4) return;

      const [x1, y1, x2, y2] = bbox;
      const color = diseaseColors[disease_type] || diseaseColors["默认"];
      const severityColor = severityColors[severity] || severityColors["mild"];

      // 绘制边界框
      ctx.strokeStyle = color;
      ctx.lineWidth = 3;
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

      // 绘制填充背景
      ctx.fillStyle = color + "40"; // 20% opacity
      ctx.fillRect(x1, y1, x2 - x1, y2 - y1);

      // 绘制标签背景
      if (showLabels) {
        const label = `${disease_type}`;
        const confLabel = showConfidence ? ` ${(confidence * 100).toFixed(1)}%` : "";
        const fullLabel = label + confLabel;

        ctx.font = "bold 14px Arial";
        const textWidth = ctx.measureText(fullLabel).width;
        const labelPadding = 4;
        const labelHeight = 20;

        // 标签背景
        ctx.fillStyle = color;
        ctx.fillRect(x1, y1 - labelHeight - labelPadding, textWidth + labelPadding * 2, labelHeight + labelPadding);

        // 标签文字
        ctx.fillStyle = "#FFFFFF";
        ctx.fillText(fullLabel, x1 + labelPadding, y1 - labelPadding / 2);
      }

      // 绘制严重程度指示器
      const indicatorSize = 10;
      ctx.beginPath();
      ctx.arc(x2 - indicatorSize / 2, y2 + indicatorSize / 2, indicatorSize, 0, Math.PI * 2);
      ctx.fillStyle = severityColor;
      ctx.fill();
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.stroke();
    });
  }, [detections, imageSize, imageLoaded, showLabels, showConfidence]);

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">检测结果</CardTitle>
      </CardHeader>
      <CardContent>
        <div ref={containerRef} className="relative overflow-hidden rounded-lg">
          {/* 图像 */}
          <img
            src={imageUrl}
            alt="Detection result"
            className="w-full h-auto"
            style={{ display: imageLoaded ? "block" : "none" }}
          />

          {/* Canvas 叠加层 */}
          <canvas
            ref={canvasRef}
            className="absolute top-0 left-0 w-full h-full"
            style={{ pointerEvents: "none" }}
          />

          {/* 加载状态 */}
          {!imageLoaded && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
              <div className="text-gray-400">加载中...</div>
            </div>
          )}
        </div>

        {/* 检测结果列表 */}
        {detections.length > 0 && (
          <div className="mt-4 space-y-2">
            {detections.map((detection, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{
                      backgroundColor:
                        diseaseColors[detection.disease_type] || diseaseColors["默认"],
                    }}
                  />
                  <div>
                    <div className="font-medium">{detection.disease_name}</div>
                    {detection.description && (
                      <div className="text-sm text-gray-500">{detection.description}</div>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-lg">
                    {(detection.confidence * 100).toFixed(1)}%
                  </div>
                  <div
                    className="text-xs px-2 py-0.5 rounded-full"
                    style={{
                      backgroundColor:
                        severityColors[detection.severity] + "20",
                      color: severityColors[detection.severity],
                    }}
                  >
                    {detection.severity === "mild"
                      ? "轻微"
                      : detection.severity === "moderate"
                      ? "中等"
                      : "严重"}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {detections.length === 0 && imageLoaded && (
          <div className="mt-4 text-center text-gray-500">
            未检测到病害
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// 导出单独的函数组件
export default DetectionVisualizer;
