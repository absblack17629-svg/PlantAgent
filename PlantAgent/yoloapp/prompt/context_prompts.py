# -*- coding: utf-8 -*-
"""
ContextAgent 提示词

用于上下文压缩、摘要和用户偏好分析的提示词模板
"""

CONTEXT_SYSTEM_PROMPT = """你是一个对话分析专家，负责对多轮对话进行压缩和摘要。

## 核心职责
1. **对话轮次判断**：判断是否需要进行压缩（≥3轮启用）
2. **对话摘要**：提取多轮对话中的关键信息，压缩成简洁摘要
3. **偏好分析**：分析用户的提问偏好和模式

## 压缩规则
- 对话 < 3轮：跳过压缩，原样传递
- 对话 ≥ 3轮：进行压缩摘要

## 摘要要求
保留以下关键信息：
1. 用户意图演变（如：从检测→查询→治疗建议）
2. 关键实体（病害名称、图片、分析结果）
3. 已完成的操作和结果
4. 未解决的问题
5. 用户关注点

## 偏好分析
分析用户的：
1. 提问类型偏好（检测型/查询型/治疗型）
2. 信息详细程度偏好
3. 关注点（防治/诊断/品种/天气等）
4. 对话风格

## 输出格式
返回JSON格式的摘要和偏好分析结果。"""

CONTEXT_COMPRESSION_TEMPLATE = """请对以下多轮对话进行压缩摘要：

对话历史（共{turn_count}轮）：
{history}

当前最新请求：
{current_request}

请返回JSON格式：
{{
    "summary": "压缩后的摘要（100字以内）",
    "key_entities": ["关键实体列表"],
    "user_intent_evolution": "意图演变",
    "completed_actions": ["已完成操作"],
    "pending_issues": ["待解决问题"],
    "focus_points": ["用户关注点"]
}}"""

CONTEXT_PREFERENCE_ANALYSIS_TEMPLATE = """请分析用户的提问偏好：

对话历史：
{history}

请返回JSON格式：
{{
    "question_type_preference": "主要提问类型（detection/query/treatment/general）",
    "detail_level_preference": "信息详细程度偏好（brief/detailed/comprehensive）",
    "topic_interests": ["感兴趣的话题列表"],
    "communication_style": "沟通风格偏好",
    "typical_patterns": ["典型提问模式"]
}}"""

CONTEXT_MERGE_TEMPLATE = """请将摘要整合到当前上下文：

原始状态：
- 意图: {intent}
- 图片路径: {image_path}
- 用户输入: {user_input}

对话摘要：
{summary}

偏好分析：
{preference}

请返回更新后的状态（JSON格式）：
{{
    "intent": "更新后的意图",
    "context_summary": "压缩后的摘要",
    "user_preference": "用户偏好分析",
    "needs_compression": false/true,
    "skip_reason": "如果跳过，说明原因"
}}"""

CONTEXT_SKIP_TEMPLATE = """对话轮次为{turn_count}轮，少于3轮，跳过压缩。

当前状态：
- 意图: {intent}
- 用户输入: {user_input}

直接传递当前状态，无需压缩。"""

CONTEXT_EXTRACTION_TEMPLATE = """基于以下对话历史，提取当前请求的相关上下文：

对话历史：
{history}

当前请求：
{current_request}

请提取：
1. 相关的历史信息
2. 指代关系
3. 省略的信息
4. 话题连续性"""
