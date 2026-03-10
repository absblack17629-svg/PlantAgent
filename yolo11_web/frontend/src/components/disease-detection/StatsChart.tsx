// -*- coding: utf-8 -*-
/**
 * 数据统计图表组件
 * 使用ECharts展示检测统计数据
 */

"use client";

import { useEffect, useRef, useState } from "react";
import * as echarts from "echarts";

interface DiseaseStats {
  total_detections: number;
  disease_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  avg_confidence: number;
  recent_trends: Array<{
    date: string;
    count: number;
  }>;
}

interface StatsChartProps {
  data: DiseaseStats;
  className?: string;
}

// 病害类型颜色
const diseaseColors: Record<string, string> = {
  白叶枯病: "#FF6B6B",
  稻瘟病: "#FFA500",
  褐斑病: "#4ECDC4",
  健康: "#95E1D3",
  其他: "#888888",
};

export function StatsChart({ data, className = "" }: StatsChartProps) {
  const pieChartRef = useRef<HTMLDivElement>(null);
  const trendChartRef = useRef<HTMLDivElement>(null);
  const [chartInitialized, setChartInitialized] = useState(false);

  // 初始化图表
  useEffect(() => {
    if (!data) return;

    const initCharts = async () => {
      // 动态导入ECharts
      const echarts = await import("echarts");

      // 饼图: 病害分布
      if (pieChartRef.current) {
        const pieChart = echarts.init(pieChartRef.current);
        
        const pieData = Object.entries(data.disease_distribution || {}).map(([name, value]) => ({
          name,
          value,
          itemStyle: { color: diseaseColors[name] || diseaseColors["其他"] },
        }));

        pieChart.setOption({
          title: {
            text: "病害类型分布",
            left: "center",
            textStyle: { fontSize: 14 },
          },
          tooltip: {
            trigger: "item",
            formatter: "{b}: {c} ({d}%)",
          },
          legend: {
            orient: "vertical",
            left: "left",
            top: "middle",
          },
          series: [
            {
              type: "pie",
              radius: ["40%", "70%"],
              center: ["60%", "50%"],
              avoidLabelOverlap: false,
              label: {
                show: true,
                formatter: "{b}: {d}%",
              },
              data: pieData.length > 0 ? pieData : [{ name: "暂无数据", value: 1, itemStyle: { color: "#eee" } }],
            },
          ],
        });
      }

      // 折线图: 趋势
      if (trendChartRef.current) {
        const trendChart = echarts.init(trendChartRef.current);
        
        const dates = data.recent_trends?.map((t) => t.date) || [];
        const counts = data.recent_trends?.map((t) => t.count) || [];

        trendChart.setOption({
          title: {
            text: "检测趋势",
            left: "center",
            textStyle: { fontSize: 14 },
          },
          tooltip: {
            trigger: "axis",
          },
          grid: {
            left: "3%",
            right: "4%",
            bottom: "3%",
            containLabel: true,
          },
          xAxis: {
            type: "category",
            data: dates.length > 0 ? dates : ["暂无数据"],
            boundaryGap: false,
          },
          yAxis: {
            type: "value",
            minInterval: 1,
          },
          series: [
            {
              name: "检测次数",
              type: "line",
              smooth: true,
              data: counts.length > 0 ? counts : [0],
              areaStyle: {
                color: "rgba(64, 158, 255, 0.2)",
              },
              itemStyle: {
                color: "#4096FF",
              },
              lineStyle: {
                width: 2,
              },
            },
          ],
        });
      }

      setChartInitialized(true);
    };

    initCharts();

    // 响应式调整
    const handleResize = () => {
      // 重新调整图表大小
    };

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [data]);

  if (!data) {
    return (
      <div className={`flex items-center justify-center h-64 ${className}`}>
        <div className="text-gray-400">暂无统计数据</div>
      </div>
    );
  }

  return (
    <div className={className}>
      {/* 统计概览 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-blue-600">{data.total_detections || 0}</div>
          <div className="text-sm text-gray-600">总检测次数</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-green-600">
            {((data.avg_confidence || 0) * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-600">平均置信度</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 text-center">
          <div className="text-3xl font-bold text-purple-600">
            {Object.keys(data.disease_distribution || {}).length}
          </div>
          <div className="text-sm text-gray-600">病害类型数</div>
        </div>
      </div>

      {/* 图表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div ref={pieChartRef} className="h-64" />
        <div ref={trendChartRef} className="h-64" />
      </div>
    </div>
  );
}

// 单独的柱状图组件
export function StatsBarChart({ data, className = "" }: { data: Record<string, number>; className?: string }) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data) return;

    const initChart = async () => {
      const echarts = await import("echarts");
      const chart = echarts.init(chartRef.current);

      const chartData = Object.entries(data).map(([name, value]) => ({
        name,
        value,
        itemStyle: { color: diseaseColors[name] || diseaseColors["其他"] },
      }));

      chart.setOption({
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "shadow" },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "category",
          data: chartData.map((d) => d.name),
          axisLabel: { interval: 0 },
        },
        yAxis: {
          type: "value",
        },
        series: [
          {
            name: "检测次数",
            type: "bar",
            data: chartData,
            barWidth: "60%",
          },
        ],
      });
    };

    initChart();
  }, [data]);

  return <div ref={chartRef} className={`h-64 ${className}`} />;
}

export default StatsChart;
