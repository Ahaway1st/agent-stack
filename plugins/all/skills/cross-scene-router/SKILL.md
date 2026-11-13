---
name: cross-scene-router
description: 综合套装的元技能：同一会话/仓库里同时有开发与视频任务时做任务路由与上下文隔离——判断当前子任务属于哪条链、加载哪套技能、产物放哪、哪些上下文禁止串用。触发：混合任务（如给刚开发的功能录演示视频、边改代码边出教程片）。不触发：纯单一场景任务。
---

# cross-scene-router

## 路由规则
1. **先分拣**：把用户的请求拆成子任务，逐个标注所属链（dev / video / base 通用）。分不清的先问一句，不默认。
2. **按链加载**：dev 子任务只走 dev 套装的流程（plan-spec → tdd-implement → code-review / ci-check）；video 子任务走 brief-analysis → storyboard-prompt → generation-orchestration → ffmpeg-post。base 的 repo-context、long-task-state、cost-visibility 两条链共用。
3. **上下文隔离**：一条链的中间结论不直接当另一条链的事实用。例如代码里的功能细节用于视频脚本前，先从已确认的规格/实际界面核对，不拿开发中的假设当卖点写进视频。
4. **产物隔离**：代码变更走代码仓库的提交流程；视频产物进媒体目录与制作单体系。演示视频引用的产品状态必须是已提交/已验证的版本，不录正在改一半的界面。
5. **状态共用一份**：混合任务用同一份 TASK-STATE.md，但计划按链分段写，进度互不冒充——视频做完不等于功能做完。

## 汇报
向用户汇报时按链分开报进度与成本（cost-visibility 的账本分开记两条链），最后给一句整体状态。任何一条链阻塞，单独说明，不拖住另一条链的交付。
