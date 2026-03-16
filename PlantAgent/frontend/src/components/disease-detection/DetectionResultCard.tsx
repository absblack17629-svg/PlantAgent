// -*- coding: utf-8 -*-
/**
 * 检测结果卡片组件
 * 显示检测结果、防治方案和详细信息
 */

"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  AlertTriangle,
  CheckCircle,
  Info,
  Shield,
  Leaf,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

interface DetectionResult {
  success: boolean;
  disease_found: boolean;
  disease_type: string;
  confidence: number;
  severity: string;
  detections: any[];
  prevention_scheme?: string;
  detection_time: string;
  duration_ms: number;
  model_version: string;
}

interface DetectionResultCardProps {
  result: DetectionResult;
  className?: string;
}

export function DetectionResultCard({ result, className = "" }: DetectionResultCardProps) {
  const [showScheme, setShowScheme] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyScheme = async () => {
    if (result.prevention_scheme) {
      await navigator.clipboard.writeText(result.prevention_scheme);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // 严重程度配置
  const severityConfig = {
    mild: { label: "轻微", color: "bg-green-100 text-green-800", icon: CheckCircle },
    moderate: { label: "中等", color: "bg-yellow-100 text-yellow-800", icon: AlertTriangle },
    severe: { label: "严重", color: "bg-red-100 text-red-800", icon: AlertTriangle },
    none: { label: "正常", color: "bg-blue-100 text-blue-800", icon: CheckCircle },
  };

  const severity = severityConfig[result.severity as keyof typeof severityConfig] || severityConfig.none;
  const SeverityIcon = severity.icon;

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            {result.disease_found ? (
              <>
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                病害检测结果
              </>
            ) : (
              <>
                <CheckCircle className="h-5 w-5 text-green-500" />
                健康状态
              </>
            )}
          </CardTitle>
          <Badge className={severity.color}>
            <SeverityIcon className="h-3 w-3 mr-1" />
            {severity.label}
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        {/* 主要检测结果 */}
        <div className="space-y-4">
          {/* 病害信息 */}
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div>
              <div className="text-sm text-gray-500">检测结果</div>
              <div className="text-xl font-bold">{result.disease_type}</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">置信度</div>
              <div className="text-2xl font-bold text-primary">
                {(result.confidence * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {/* 元信息 */}
          <div className="flex gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <Leaf className="h-4 w-4" />
              {result.model_version="YOLO-SGHM"}
            </div>
            <div>
              检测耗时: {result.duration_ms}ms
            </div>
          </div>

          {/* 防治方案 */}
          {result.prevention_scheme && result.disease_found && (
            <div className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-between"
                onClick={() => setShowScheme(!showScheme)}
              >
                <span className="flex items-center gap-2">
                  <Shield className="h-4 w-4" />
                  防治方案
                </span>
                {showScheme ? (
                  <ChevronUp className="h-4 w-4" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
              </Button>

              {showScheme && (
                <div className="relative">
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200 max-h-96 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm font-medium text-green-800">
                      {result.prevention_scheme}
                    </pre>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="absolute top-2 right-2"
                    onClick={handleCopyScheme}
                  >
                    {copied ? (
                      <Check className="h-4 w-4 text-green-500" />
                    ) : (
                      <Copy className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* 健康建议 */}
          {!result.disease_found && (
            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start gap-3">
                <Info className="h-5 w-5 text-blue-500 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-800">水稻生长正常</div>
                  <div className="text-sm text-blue-600 mt-1">
                    继续保持良好的田间管理，定期观察水稻生长情况，提前预防病害发生。
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default DetectionResultCard;
