# Uber Michelangelo Platform 与模型服务抽象

## 企业背景

**公司：** Uber Technologies
**规模：** 全球最大网约车和配送平台，日均 2300 万次行程（2023）
**技术挑战：** 需要部署和管理数千个机器学习模型，支撑实时定价、ETA 预测、路线优化等核心业务

## 技术问题

### 碎片化的模型部署

**2016 年前 Uber 的痛点：**

1. **每个团队自建模型基础设施**
   - 推荐团队用 TensorFlow + 自建服务
   - 定价团队用 XGBoost + 自己的 API
   - 预测团队用 Python + Flask

2. **重复工作**
   - 每个团队重写数据预处理
   - 每个团队重写模型服务化
   - 每个团队重写监控和日志

3. **无法测试**
   - 测试必须部署真实模型
   - A/B 测试成本高
   - 难以回滚

### Uber 的解决方案：Michelangelo 平台

**核心设计：** 统一的 ML 生命周期管理平台

```
┌────────────────────────────────────────────────┐
│            Michelangelo Platform                │
├────────────────────────────────────────────────┤
│  训练 → 评估 → 部署 → 预测 → 监控              │
└────────────────────────────────────────────────┘
                    ▲
                    │ 统一接口
        ┌───────────┼───────────┐
        │           │           │
    TensorFlow   XGBoost    PyTorch
```

**关键组件：**

1. **Model Service 抽象层**
   ```python
   # 统一的预测接口（伪代码）
   class ModelService:
       def predict(self, features: Dict) -> Dict:
           """所有模型都实现这个接口"""
           pass
   ```

2. **Model Type Adapter**
   ```python
   class TensorFlowAdapter(ModelService):
       def predict(self, features):
           # 1. 转换特征格式
           tensor_input = self._to_tensor(features)
           # 2. 调用 TF 模型
           output = self.tf_model.run(tensor_input)
           # 3. 转换输出格式
           return self._to_dict(output)
   
   class XGBoostAdapter(ModelService):
       def predict(self, features):
           # 同样的接口，不同的实现
           pass
   ```

3. **Mock Prediction Service**
   ```python
   class MockModelService(ModelService):
       def predict(self, features):
           # 测试时返回固定结果
           return {"price": 15.50}
   ```

**技术实现细节：**

```python
# 业务代码不知道用的是什么模型
def calculate_surge_pricing(location, time):
    model = ModelRegistry.get("surge_pricing_v3")
    features = {
        "lat": location.lat,
        "lon": location.lon,
        "hour": time.hour,
        "demand": get_current_demand(location)
    }
    prediction = model.predict(features)
    return prediction["surge_multiplier"]
```

## 技术成果

### 1. 规模化

- **模型数量：** 从几十个增长到数千个
- **团队效率：** 模型上线时间从数周缩短到数天
- **成本降低：** 共享基础设施，避免重复建设

### 2. 可测试性

**A/B 测试：**
```python
# 生产环境同时运行多个模型版本
if user_id % 100 < 10:
    model = ModelRegistry.get("surge_v4_experimental")
else:
    model = ModelRegistry.get("surge_v3_stable")
```

**离线评估：**
```python
# 用历史数据测试新模型
test_model = MockModelService(predictions_from_csv)
metrics = evaluate(test_model, test_dataset)
```

### 3. 2017 年生产事故案例

**问题：** 某个 XGBoost 模型更新后，预测延迟从 10ms 飙升到 500ms

**快速定位：**
- 统一的监控看到 `surge_pricing_v3` 延迟异常
- 日志显示特征预处理逻辑变慢
- 通过 Model Registry 立即回滚到 v2

**如果没有 Michelangelo：**
- 需要排查多个服务
- 回滚需要重新部署
- 可能影响数百万用户

## 与 ClawBot 的技术关联

| Uber Michelangelo | ClawBot 对应实现 | 原理相同点 |
|------------------|-----------------|-----------|
| **统一预测接口** `predict(features)` | 统一模型协议 `model(messages)` | 业务代码不关心底层实现 |
| **Model Type Adapter** (TF/XGBoost) | Model Adapter (OpenAI/Claude) | 把不同供应商适配到统一接口 |
| **Mock Prediction Service** | Fake Model | 测试时不依赖真实服务 |
| **Model Registry** | `OpenAICompatibleModel.from_env()` | 配置驱动，不硬编码 |
| **A/B Testing** | 轻松切换 model 参数（未来） | 依赖注入让切换简单 |

### 代码示例对比

**Uber Michelangelo 模式：**
```python
# 业务层
pricing = calculate_surge(location, time)

# 框架层
def calculate_surge(location, time):
    model = ModelRegistry.get("surge_v3")
    features = extract_features(location, time)
    return model.predict(features)  # 统一接口

# 适配器层
class XGBoostAdapter:
    def predict(self, features):
        # XGBoost 特定逻辑
        pass
```

**ClawBot 模式：**
```python
# 业务层
answer = analyze_code(code)

# 框架层
def analyze_code(code):
    model = OpenAICompatibleModel.from_env()
    harness = Harness(model, system_prompt="...")
    return harness.run(code)  # 统一接口

# 适配器层
class OpenAICompatibleModel:
    def __call__(self, messages):
        # OpenAI 特定逻辑
        pass
```

**相同点：**
- 三层架构：业务 → 框架 → 适配器
- 统一接口隔离变化
- 测试时用 Mock/Fake
- 配置驱动（不硬编码供应商）

## 面试中怎么讲

### 场景 1：系统设计面试

**问题：** "设计一个 ML 模型服务平台"

**回答（引用 Uber）：**

> "我会参考 Uber Michelangelo 的设计：
> 
> **核心挑战：**
> 1. 不同团队用不同框架（TensorFlow, PyTorch, XGBoost）
> 2. 每个团队重复建设模型服务基础设施
> 3. 测试和 A/B 实验成本高
> 
> **解决方案：**
> 
> **1. 统一预测接口**
> ```python
> class ModelService(ABC):
>     @abstractmethod
>     def predict(self, features: Dict) -> Dict:
>         pass
> ```
> 
> **2. 适配器模式**
> - TensorFlowAdapter 处理张量转换
> - XGBoostAdapter 处理矩阵格式
> - 业务代码只知道 `predict()` 接口
> 
> **3. Mock Service**
> - 测试时用 MockModelService 返回固定结果
> - 不需要真实模型，快速验证逻辑
> 
> **4. Model Registry**
> - 配置驱动选择模型版本
> - 支持 A/B 测试和快速回滚
> 
> 我在 ClawBot 项目中实现了类似的设计，只是把'模型'从 ML 模型换成了 LLM。"

### 场景 2：项目深度追问

**问题：** "你的适配器设计参考了哪些实际案例？"

**回答：**

> "主要参考了 Uber Michelangelo 的 Model Type Adapter 设计。
> 
> **Uber 的做法：**
> - 定义统一的 `predict(features)` 接口
> - 每种模型类型有一个 Adapter（TensorFlow, XGBoost, PyTorch）
> - Adapter 负责格式转换、模型调用、输出解析
> - 业务代码通过 Model Registry 获取模型，不直接依赖具体类型
> 
> **我在 ClawBot 中的应用：**
> - 定义统一的 `model(messages) -> string` 协议
> - `OpenAICompatibleModel` 是一个 Adapter，处理 HTTP 请求和 JSON 解析
> - 未来可以加 `ClaudeAdapter`, `LocalLLamaAdapter`
> - Harness 只依赖协议，不关心底层是哪个供应商
> 
> **关键收益：**
> - 测试时用 Fake Model（类似 Uber 的 Mock Service）
> - 切换供应商不改 Harness 代码
> - 其他项目可以直接复用 Harness"

### 场景 3：行为面试

**问题：** "描述一次你从业界实践中学到的经验"

**回答（STAR）：**

> **Situation:** 在设计 ClawBot 的模型抽象时，我一开始想直接集成 OpenAI SDK。
> 
> **Task:** 但我意识到这样会让 Harness 和 OpenAI 强耦合，未来难以扩展。
> 
> **Action:** 我研究了 Uber Michelangelo 的论文和技术博客，学习他们如何在一个平台上支持多种 ML 框架。关键启发是：
> 1. 不要让核心依赖具体实现
> 2. 用适配器隔离变化
> 3. 用 Mock 服务让测试独立
> 
> 我把这个思想应用到 ClawBot：
> - Harness 只依赖 `messages -> string` 协议
> - `OpenAICompatibleModel` 作为适配器
> - Fake Model 让测试不需要 API key
> 
> **Result:** 最终设计非常灵活，我可以轻松添加其他供应商的 Adapter，而且整个项目可以完全离线测试。这次经历让我理解了'从优秀工程实践中学习'比'自己想当然设计'更有效。"

## 简历中可以这样写

**项目描述：**
> ClawBot - AI Agent Harness 框架
> 
> 参考 Uber Michelangelo 平台的模型服务抽象设计，实现了支持多供应商的 LLM 适配器层。通过依赖倒置原则和测试替身，实现了零运行时依赖的可复用框架。

**技术亮点：**
> 借鉴 Uber Michelangelo 的 Model Type Adapter 设计，实现了 OpenAI-compatible 适配器，支持任意兼容供应商无缝切换，测试时用 Fake Model 替换真实 API

## 延伸阅读

**官方资源：**
- [Uber Engineering Blog - Michelangelo](https://www.uber.com/blog/michelangelo-machine-learning-platform/)
- [Meet Michelangelo: Uber's ML Platform](https://eng.uber.com/michelangelo-machine-learning-platform/)

**关键论文：**
- Herman et al. "Michelangelo: Uber's Machine Learning Platform" (2018)

**相似平台：**
- Google Vertex AI
- AWS SageMaker
- Microsoft Azure ML

**ClawBot 对应代码：**
- 适配器实现：`clawbot/models.py:23-127`
- 统一协议：`clawbot/agent.py:7`
- Fake Model：`tests/test_agent.py:8-10`

## 练习题

1. **设计题：** 如果要添加一个 Claude API 的适配器，需要改动哪些代码？Harness 需要改吗？

2. **对比题：** Uber 的 Model Registry 和 ClawBot 的 `from_env()` 工厂方法，有什么相同点和不同点？

3. **实现题：** 实现一个 `CachedModel` 装饰器，在适配器外面加一层缓存，相同输入直接返回缓存结果。

4. **架构题：** 如果需要支持 A/B 测试（10% 用户用 GPT-4，90% 用 GPT-3.5），怎样设计？
