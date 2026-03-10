"use client";

import { useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const pages = [
  { id: "home", name: "首页", icon: "fa-home", url: "/" },
  { id: "detect", name: "病害检测", icon: "fa-microscope", url: "/detect" },
  { id: "news", name: "知识资讯", icon: "fa-newspaper", url: "/news" },
  { id: "agent", name: "智能助手", icon: "fa-robot", url: "/agent" },
  { id: "history", name: "浏览历史", icon: "fa-history", url: "/history" },
  { id: "profile", name: "个人中心", icon: "fa-user", url: "/profile" },
];

export default function HomePage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState("home");
  const [iframeKey, setIframeKey] = useState(0);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const page = searchParams.get("page") || "home";
    setCurrentPage(page);
    setIframeKey((k) => k + 1);
  }, [searchParams]);

  // 检查登录状态
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      fetch(`${API_URL}/api/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((r) => r.json())
        .then((data) => {
          if (data.username) setUser(data);
        })
        .catch(() => {});
    }
  }, []);

  const navigateTo = (pageId: string) => {
    router.push(`/?page=${pageId}`);
  };

  const getPageUrl = () => {
    // 这些页面使用 Next.js 路由，不需要 iframe
    const nextJsPages = ["detect", "status"];
    if (nextJsPages.includes(currentPage)) {
      return null; // 返回 null 表示使用 Next.js 路由
    }
    
    // 其他页面使用 iframe 加载后端 HTML
    switch (currentPage) {
      case "home":
        return `${API_URL}/`;
      case "news":
        return `${API_URL}/news`;
      case "agent":
        return `${API_URL}/agent`;
      case "history":
        return `${API_URL}/user/history`;
      case "profile":
        return `${API_URL}/profile`;
      case "login":
        return `${API_URL}/login`;
      case "register":
        return `${API_URL}/register`;
      default:
        return `${API_URL}/`;
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUser(null);
    router.push("/?page=login");
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* 左侧导航栏 */}
      <div
        style={{
          width: "200px",
          background: "linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)",
          color: "white",
          display: "flex",
          flexDirection: "column",
          padding: "20px 0",
        }}
      >
        {/* Logo */}
        <div
          style={{
            padding: "0 20px 30px",
            borderBottom: "1px solid rgba(255,255,255,0.1)",
            marginBottom: "20px",
          }}
        >
          <h1 style={{ fontSize: "18px", fontWeight: "bold" }}>
            🌾 水稻病害系统
          </h1>
          <p style={{ fontSize: "12px", opacity: 0.6, marginTop: "5px" }}>
            YOLO11 Smart Agriculture
          </p>
        </div>

        {/* 导航菜单 */}
        <nav style={{ flex: 1 }}>
          {pages.map((page) => (
            <button
              key={page.id}
              onClick={() => navigateTo(page.id)}
              style={{
                width: "100%",
                padding: "12px 20px",
                background: currentPage === page.id ? "rgba(255,255,255,0.1)" : "transparent",
                border: "none",
                color: currentPage === page.id ? "#4ade80" : "white",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "10px",
                fontSize: "14px",
                textAlign: "left",
                transition: "all 0.2s",
              }}
            >
              <i className={`fas ${page.icon}`} style={{ width: "20px" }}></i>
              {page.name}
            </button>
          ))}
        </nav>

        {/* 用户信息 */}
        <div
          style={{
            padding: "20px",
            borderTop: "1px solid rgba(255,255,255,0.1)",
          }}
        >
          {user ? (
            <div>
              <p style={{ fontSize: "12px", opacity: 0.6 }}>欢迎，{user.username}</p>
              <button
                onClick={handleLogout}
                style={{
                  marginTop: "10px",
                  padding: "8px 16px",
                  background: "rgba(255,255,255,0.1)",
                  border: "none",
                  color: "white",
                  cursor: "pointer",
                  borderRadius: "4px",
                  fontSize: "12px",
                }}
              >
                退出登录
              </button>
            </div>
          ) : (
            <button
              onClick={() => navigateTo("login")}
              style={{
                width: "100%",
                padding: "10px",
                background: "#4ade80",
                border: "none",
                color: "#1a1a2e",
                cursor: "pointer",
                borderRadius: "6px",
                fontWeight: "bold",
              }}
            >
              登录 / 注册
            </button>
          )}
        </div>
      </div>

      {/* 右侧内容区 */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {/* 顶部栏 */}
        <div
          style={{
            height: "50px",
            background: "white",
            borderBottom: "1px solid #e5e7eb",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            padding: "0 20px",
          }}
        >
          <span style={{ fontSize: "14px", color: "#6b7280" }}>
            {pages.find((p) => p.id === currentPage)?.name || "首页"}
          </span>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "12px", color: "#6b7280" }}>
              后端: {API_URL}
            </span>
          </div>
        </div>

        {/* iframe 内容区或 Next.js 页面 */}
        {getPageUrl() === null ? (
          // 使用 Next.js 路由的页面
          <div style={{ flex: 1, overflow: "auto" }}>
            {currentPage === "detect" && (
              <iframe
                key={iframeKey}
                src="/detect"
                style={{
                  width: "100%",
                  height: "100%",
                  border: "none",
                  background: "#f9fafb",
                }}
                title="detect"
              />
            )}
            {currentPage === "status" && (
              <iframe
                key={iframeKey}
                src="/status"
                style={{
                  width: "100%",
                  height: "100%",
                  border: "none",
                  background: "#f9fafb",
                }}
                title="status"
              />
            )}
          </div>
        ) : (
          // 使用 iframe 加载后端页面
          <iframe
            key={iframeKey}
            src={getPageUrl()!}
            style={{
              flex: 1,
              width: "100%",
              border: "none",
              background: "#f9fafb",
            }}
            title={currentPage}
          />
        )}
      </div>
    </div>
  );
}
