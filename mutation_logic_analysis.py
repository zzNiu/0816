# 变异逻辑分析工具
import random
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict, Counter

def analyze_current_mutation_logic():
    """分析当前变异逻辑的特点"""
    print("=" * 60)
    print("🔍 当前变异逻辑分析")
    print("=" * 60)
    
    print("\n📋 变异策略概览:")
    print("1. 🚗 车头时距变异 (独立进行)")
    print("   - 策略: 局部变异 ±3")
    print("   - 约束: [min_headway, max_headway]")
    print("   - 频率: 每个车辆按 mutpb 概率变异")
    
    print("\n2. 🎲 选择性模块变异 (二选一)")
    print("   - 初始配置变异 (50%概率)")
    print("     * 随机选择一个车辆")
    print("     * 完全重新生成模块配置")
    print("     * 需要重新生成 module_adjustments")
    print("   - 模块调整变异 (50%概率)")
    print("     * 随机选择一个车辆一个站点")
    print("     * 基于 adjustment_ranges 约束变异")
    print("     * 直接修改 delta_p 和 delta_f")

def simulate_mutation_behavior(num_simulations=1000):
    """模拟变异行为统计"""
    print("\n" + "=" * 60)
    print("📊 变异行为统计分析")
    print("=" * 60)
    
    # 模拟参数
    mutpb = 0.3  # 变异概率
    num_vehicles = 5
    min_headway, max_headway = 3, 20
    
    # 统计数据
    headway_changes = []
    mutation_types = []
    headway_mutation_count = 0
    
    for _ in range(num_simulations):
        # 1. 车头时距变异统计
        headway_mutations = 0
        for vehicle_id in range(num_vehicles * 2):  # up + down
            if random.random() < mutpb:
                current_headway = random.randint(min_headway, max_headway)
                adjustment = random.randint(-3, 3)
                new_headway = max(min_headway, min(max_headway, current_headway + adjustment))
                headway_changes.append(abs(new_headway - current_headway))
                headway_mutations += 1
        
        headway_mutation_count += headway_mutations
        
        # 2. 模块变异类型统计
        mutate_type = random.randint(0, 1)
        mutation_types.append("初始配置" if mutate_type == 0 else "模块调整")
    
    # 分析结果
    print(f"\n📈 车头时距变异统计 (基于 {num_simulations} 次模拟):")
    print(f"   平均每次变异影响车辆数: {headway_mutation_count / num_simulations:.2f}")
    print(f"   平均变化幅度: {np.mean(headway_changes):.2f}")
    print(f"   变化范围: {min(headway_changes)} - {max(headway_changes)}")
    
    print(f"\n🎯 模块变异类型分布:")
    type_counts = Counter(mutation_types)
    for mut_type, count in type_counts.items():
        print(f"   {mut_type}: {count}/{num_simulations} ({count/num_simulations*100:.1f}%)")

def analyze_mutation_effectiveness():
    """分析变异有效性"""
    print("\n" + "=" * 60)
    print("⚡ 变异有效性分析")
    print("=" * 60)
    
    print("\n✅ 当前逻辑的优点:")
    print("1. 🎯 避免逻辑冲突")
    print("   - 不再同时变异初始配置和模块调整")
    print("   - 解决了重复计算问题")
    
    print("2. 🔧 精确变异控制")
    print("   - 每次只变异一个车辆的初始配置")
    print("   - 每次只变异一个站点的模块调整")
    print("   - 减少了变异的破坏性")
    
    print("3. 🚗 车头时距独立变异")
    print("   - 不影响模块配置")
    print("   - 保持时间约束的一致性")
    
    print("\n⚠️ 潜在问题:")
    print("1. 🐌 变异强度可能不足")
    print("   - 每次只变异一个元素")
    print("   - 可能导致收敛过慢")
    print("   - 探索能力有限")
    
    print("2. 🔄 缺少重新生成机制")
    print("   - 初始配置变异后没有重新生成 module_adjustments")
    print("   - adjustment_ranges 可能过时")
    print("   - 影响后续模块调整变异的准确性")
    
    print("3. 📊 缺少自适应机制")
    print("   - 变异概率和强度固定")
    print("   - 没有根据进化阶段调整")
    print("   - 无法适应不同问题特征")

def suggest_improvements():
    """提出改进建议"""
    print("\n" + "=" * 60)
    print("🚀 改进建议")
    print("=" * 60)
    
    print("\n1. 🔄 添加重新生成机制")
    print("   ```python")
    print("   if need_recalculate_ranges:")
    print("       updated_individual = regenerate_module_adjustments_for_individual(")
    print("           individual, parameters, global_demand_data)")
    print("       # 更新 module_adjustments 和 adjustment_ranges")
    print("   ```")
    
    print("\n2. 📈 自适应变异强度")
    print("   ```python")
    print("   # 根据进化代数调整变异强度")
    print("   generation_ratio = current_gen / max_gen")
    print("   if generation_ratio < 0.3:")
    print("       mutation_strength *= 1.5  # 早期增强探索")
    print("   elif generation_ratio > 0.7:")
    print("       mutation_strength *= 0.7  # 后期精细调优")
    print("   ```")
    
    print("\n3. 🎯 多元素变异选项")
    print("   ```python")
    print("   # 根据情况选择变异多个元素")
    print("   if random.random() < 0.3:  # 30%概率进行多元素变异")
    print("       num_mutations = random.randint(2, 3)")
    print("       # 变异多个车辆或站点")
    print("   ```")
    
    print("\n4. 🔍 变异效果监控")
    print("   ```python")
    print("   # 记录变异前后的适应度变化")
    print("   mutation_history = {")
    print("       'type': mutation_type,")
    print("       'fitness_before': old_fitness,")
    print("       'fitness_after': new_fitness")
    print("   }")
    print("   ```")

def create_mutation_flow_diagram():
    """创建变异流程图"""
    print("\n" + "=" * 60)
    print("📊 变异流程图")
    print("=" * 60)
    
    print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                    intelligent_mutate                      │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │              1. 车头时距变异                                │
    │  ┌─────────────────────────────────────────────────────┐    │
    │  │ for each vehicle:                                   │    │
    │  │   if random() < mutpb:                             │    │
    │  │     new_headway = current + random(-3, 3)          │    │
    │  │     clamp to [min_headway, max_headway]            │    │
    │  └─────────────────────────────────────────────────────┘    │
    └─────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────▼───────────────────────────────────────┐
    │              2. 选择变异类型                                │
    │                random.randint(0, 1)                        │
    └─────────────┬───────────────────────────┬───────────────────┘
                  │                           │
    ┌─────────────▼─────────────┐   ┌─────────▼─────────────────────┐
    │     初始配置变异          │   │      模块调整变异             │
    │  ┌─────────────────────┐  │   │  ┌─────────────────────────┐  │
    │  │ 随机选择一个车辆    │  │   │  │ 随机选择一个车辆+站点   │  │
    │  │ 重新生成模块配置    │  │   │  │ 基于ranges变异delta值   │  │
    │  │ need_recalculate=T  │  │   │  │ 直接修改adjustments     │  │
    │  └─────────────────────┘  │   │  └─────────────────────────┘  │
    └─────────────┬─────────────┘   └─────────────┬─────────────────┘
                  │                               │
    ┌─────────────▼───────────────────────────────▼─────────────────┐
    │                    3. 返回个体                               │
    │              ⚠️ 缺少重新生成逻辑                             │
    └─────────────────────────────────────────────────────────────┘
    """)

if __name__ == "__main__":
    analyze_current_mutation_logic()
    simulate_mutation_behavior()
    analyze_mutation_effectiveness()
    suggest_improvements()
    create_mutation_flow_diagram()
    
    print("\n" + "=" * 60)
    print("📝 总结")
    print("=" * 60)
    print("当前变异逻辑已经解决了之前的逻辑冲突问题，")
    print("但仍需要添加重新生成机制和自适应策略来提高效果。")
    print("建议优先实现重新生成机制，确保变异的一致性。")
