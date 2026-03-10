// -*- coding: utf-8 -*-
/**
 * 图像上传与预处理组件
 * 支持拖拽上传、裁剪、旋转等预处理
 */

"use client";

import { useState, useRef, useCallback } from "react";
import { Upload, Image as ImageIcon, X, Crop, RotateCw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface ImageUploadProps {
  onImageSelect: (file: File, previewUrl: string) => void;
  accept?: string;
  maxSize?: number;
  disabled?: boolean;
}

export function ImageUpload({
  onImageSelect,
  accept = "image/png,image/jpeg,image/jpg,image/webp",
  maxSize = 10 * 1024 * 1024, // 10MB
  disabled = false,
}: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): boolean => {
    // 检查文件类型
    const allowedTypes = accept.split(",").map((t) => t.trim());
    if (!allowedTypes.some((type) => file.type === type || file.type.match(type.replace("*", ".*")))) {
      setError("不支持的文件格式，请上传 PNG、JPG 或 WebP 格式的图片");
      return false;
    }

    // 检查文件大小
    if (file.size > maxSize) {
      setError(`文件大小不能超过 ${Math.round(maxSize / 1024 / 1024)}MB`);
      return false;
    }

    return true;
  };

  const processFile = useCallback(
    async (file: File) => {
      if (!validateFile(file)) return;

      setIsLoading(true);
      setError(null);

      try {
        // 创建预览
        const previewUrl = URL.createObjectURL(file);
        setPreview(previewUrl);

        // 回调
        onImageSelect(file, previewUrl);
      } catch (err) {
        setError("图片处理失败，请重试");
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    },
    [onImageSelect]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleClear = () => {
    setPreview(null);
    setError(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <div className="w-full">
      {/* 上传区域 */}
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-6 text-center cursor-pointer
          transition-colors duration-200
          ${
            isDragging
              ? "border-primary bg-primary/5"
              : "border-gray-300 hover:border-gray-400"
          }
          ${disabled ? "opacity-50 cursor-not-allowed" : ""}
        `}
        onDragOver={disabled ? undefined : handleDragOver}
        onDragLeave={disabled ? undefined : handleDragLeave}
        onDrop={disabled ? undefined : handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          className="hidden"
          disabled={disabled}
        />

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-8">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <p className="mt-4 text-sm text-gray-500">正在处理图片...</p>
          </div>
        ) : preview ? (
          <div className="relative">
            <img
              src={preview}
              alt="Preview"
              className="max-h-64 mx-auto rounded-lg object-contain"
            />
            <Button
              variant="destructive"
              size="icon"
              className="absolute top-2 right-2"
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-8">
            <Upload className="h-12 w-12 text-gray-400" />
            <p className="mt-4 text-sm text-gray-600">
              拖拽图片到此处，或点击选择文件
            </p>
            <p className="mt-2 text-xs text-gray-400">
              支持 PNG、JPG、WebP 格式，最大 {Math.round(maxSize / 1024 / 1024)}MB
            </p>
          </div>
        )}
      </div>

      {/* 错误提示 */}
      {error && (
        <p className="mt-2 text-sm text-red-500">{error}</p>
      )}

      {/* 快捷操作 */}
      {preview && (
        <div className="mt-4 flex gap-2 justify-center">
          <Button
            variant="outline"
            size="sm"
            onClick={() => inputRef.current?.click()}
          >
            <ImageIcon className="h-4 w-4 mr-2" />
            重新选择
          </Button>
        </div>
      )}
    </div>
  );
}

export default ImageUpload;
