import math
import random
from deap import tools

# === 新增：读评估阶段写入的成本缓存 & 绘图函数 ===
from deap_toolbox_setup import cost_cache
from plot_cost_stack import plot_cost_stack_from_history

# 从工具箱模块拿评估期缓存（evaluate_individual 里写入）
try:
    from deap_toolbox_setup import cost_cache as EVAL_COST_CACHE
except Exception:
    EVAL_COST_CACHE = {}


def customized_genetic_algorithm(population, toolbox, cxpb, mutpb, ngen, stats=None, halloffame=None,
                           parameters=None, global_demand_data=None, max_regeneration_attempts=5, verbose=True):
    """
    Hybrid Genetic Algorithm with Regeneration Strategy for infeasible individuals.
    Uses module adjustment ranges from simulation to guide mutation and crossover.

    :param population: Initial population
    :param toolbox: DEAP toolbox (with evaluate, mate, mutate, select)
    :param cxpb: Crossover probability
    :param mutpb: Mutation probability
    :param ngen: Number of generations
    :param stats: DEAP Statistics object
    :param halloffame: DEAP HallOfFame object
    :param parameters: Custom parameters passed to evaluate
    :param global_demand_data: Custom demand data passed to evaluate
    :param max_regeneration_attempts: Maximum times to attempt regenerating an infeasible individual
    :param verbose: Whether to print log each generation
    :return: (final population, logbook)
    """

    # ===== 在 customized_genetic_algorithm.py 中（遗传主循环外侧）=====
    # === 新增：成本历史（按每代最优个体记录） ===
    cost_history = {"passenger": [], "freight": [], "mav": []}

    # === 新增：记录当前种群最优个体的三项成本 ===
    def record_best_cost(pop):
        # 过滤出已赋值适应度且有限的个体
        valid = [x for x in pop if x.fitness.valid and math.isfinite(x.fitness.values[0])]
        if not valid:
            # 没有可用个体时，记 0 占位，保证代数对齐
            for k in cost_history:
                cost_history[k].append(0.0)
            return

        # 取适应度最小（更优）的个体
        best = min(valid, key=lambda x: x.fitness.values[0])

        # 从评估阶段的缓存读取三项成本（key 用 id(best)）
        cc = cost_cache.get(id(best))
        if cc is None:
            # 极少发生：当代没命中缓存（例如该个体未被重新评估）
            for k in cost_history:
                cost_history[k].append(0.0)
            return

        cost_history["passenger"].append(float(cc.get("passenger_waiting_cost", 0.0)))
        cost_history["freight"].append(float(cc.get("freight_waiting_cost", 0.0)))
        cost_history["mav"].append(float(cc.get("mav_transport_cost", 0.0)))


    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # 初始种群评估 Evaluate initial population

    print('----进入遗传算法 步骤3： 初始种群评估----')
    i = 1
    for ind in population:
        print(f'第 {i} 个个体')
        # print('ind:', ind)
        # print('初始种群评估')
        i += 1
        fit, failure_records, module_adjustment_ranges = toolbox.evaluate(ind)
        print('fit_value:', fit)
        ind.fitness.values = fit
        # 存储模块调整范围信息到个体中，供后续变异使用
        ind.adjustment_ranges = module_adjustment_ranges

    # 记录初始种群评估结果
    feasible = [ind.fitness.values[0] for ind in population if math.isfinite(ind.fitness.values[0])]
    if feasible:
        gen_min = min(feasible)
        gen_avg = sum(feasible) / len(feasible)
        gen_max = max(feasible)
    else:
        gen_min = gen_avg = gen_max = float('nan')

    print('初始种群评估完成')

    # === 新增：记录第 0 代最优个体的成本构成 ===
    record_best_cost(population)

    logbook.record(gen=0, nevals=len(population),avg=gen_avg, min=gen_min, max=gen_max)
    if verbose:
        print(logbook.stream)


    # 种群进化Evolution loop
    print('----进入遗传算法 步骤4 种群开始进化----')
    # print('----第2步：种群开始进化----')
    for gen in range(1, ngen + 1):

        # 选择操作
        offspring = toolbox.select(population, len(population))
        offspring = list(map(toolbox.clone, offspring))

        # 变异
        for mutant in offspring:
            if random.random() < mutpb:
                print('变异了')
                # 如果个体有调整范围信息，传递给变异操作
                if hasattr(mutant, 'adjustment_ranges'):
                    toolbox.mutate(mutant, parameters, global_demand_data)
                else:
                    toolbox.mutate(mutant, parameters, global_demand_data)
                del mutant.fitness.values
                # 清除调整范围信息，因为个体已经改变
                if hasattr(mutant, 'adjustment_ranges'):
                    delattr(mutant, 'adjustment_ranges')

        # 评估和处理不可行个体
        for i, ind in enumerate(offspring):
            if not ind.fitness.valid:
                print(f"➡️ 代数 {gen}，个体 {i + 1}/{len(offspring)}：开始评估")
                
                # 尝试评估个体
                fit, failure_records, module_adjustment_ranges = toolbox.evaluate(ind)
                print(f"评估结果: {fit}")
                
                # 处理不可行个体
                if not math.isfinite(fit[0]):
                    print(f"❌ 个体 {i + 1} 不可行，尝试重新生成")

                    # 存储最佳尝试结果
                    best_ind = toolbox.clone(ind)
                    best_fit = fit
                    
                    # 尝试重新生成个体
                    for attempt in range(max_regeneration_attempts):
                        # 从可行个体中随机选择两个父本
                        feasible_parents = [p for p in population if math.isfinite(p.fitness.values[0])]
                        
                        if len(feasible_parents) >= 2:
                            # 有足够的可行父本，进行交叉和变异
                            parent1, parent2 = random.sample(feasible_parents, 2)
                            new_ind = toolbox.clone(parent1)

                            # 应用交叉
                            # if random.random() < cxpb:  # 高概率交叉
                            #     toolbox.mate(new_ind, toolbox.clone(parent2), parameters, global_demand_data)

                            # 应用变异
                            if hasattr(parent1, 'adjustment_ranges'):
                                toolbox.mutate(new_ind, parameters, global_demand_data)
                            else:
                                toolbox.mutate(new_ind, parameters, global_demand_data)
                        else:
                            # 没有足够的可行父本，生成新个体
                            new_ind = toolbox.individual()
                        
                        # 评估新个体
                        new_fit, new_failures, new_ranges = toolbox.evaluate(new_ind)
                        print(f"🔄 重生成尝试 {attempt + 1}，fit: {new_fit}")
                        
                        # 如果新个体可行或比之前的更好，则保留
                        if math.isfinite(new_fit[0]):
                        # if math.isfinite(new_fit[0]) or (not math.isfinite(best_fit[0]) and new_fit[0] < best_fit[0]):
                            best_ind = new_ind
                            best_fit = new_fit
                            best_ind.adjustment_ranges = new_ranges
                            
                            if math.isfinite(new_fit[0]):
                                print(f"✅ 生成成功，个体 {i + 1} 现在可行")
                                break
                    
                    # 使用最佳尝试结果替换当前个体
                    ind = best_ind
                    fit = best_fit
                    offspring[i] = best_ind
                else:
                    print(f"✅ 评估成功，个体 {i + 1} 可行")
                    # 存储模块调整范围信息到个体中
                    ind.adjustment_ranges = module_adjustment_ranges
                
                ind.fitness.values = fit

            else:

                print(f"个体 {i + 1} 直接继承母代")

        # 更新名人堂
        if halloffame is not None:
            halloffame.update(offspring)

        # 精英保留策略：保留一部分最好的父代个体
        elite_size = max(1, int(len(population) * 0.02))  # 保留10%的精英
        elites = tools.selBest(population, elite_size)

        # 替换种群，但保留精英
        offspring_size = len(population) - elite_size
        offspring = tools.selBest(offspring, offspring_size)  # 选择最好的后代
        population[:] = elites + offspring  # 精英 + 后代

        # # 替换种群
        # population[:] = offspring

        # 统计当前种群中所有已评估且有效的个体
        feasible = [ind.fitness.values[0]
                    for ind in population
                    if ind.fitness.valid
                    and len(ind.fitness.values) > 0
                    and math.isfinite(ind.fitness.values[0])]

        if feasible:
            gen_min = min(feasible)
            gen_avg = sum(feasible) / len(feasible)
            gen_max = max(feasible)
        else:
            gen_min = gen_avg = gen_max = float('nan')

        logbook.record(gen=gen, nevals=len(offspring),
                       avg=gen_avg, min=gen_min, max=gen_max)

        # === 新增：记录本代最优个体的成本构成 ===
        record_best_cost(population)

        if verbose:
            print(logbook.stream)

    print('进化完成')

    # === 新增：出图（文件默认名：成本构成堆叠图.png） ===
    try:
        plot_cost_stack_from_history(cost_history, title="成本构成堆叠图", save_path="best_solution_20250814_144416/成本构成堆叠图.png")
    except Exception as e:
        print(f"绘制成本堆叠图失败：{e}")

    return population, logbook, cost_history


def run_genetic_algorithm_with_initialization(population_size, num_vehicles, max_modules,
                                            toolbox, cxpb, mutpb, ngen,
                                            headway_range=(3, 20), stats=None, halloffame=None,
                                            parameters=None, global_demand_data=None, verbose=True):
    """
    运行完整的遗传算法，包括初始种群生成

    Args:
        population_size: 种群大小
        num_vehicles: 车辆数量
        max_modules: 最大模块数
        toolbox: DEAP工具箱
        cxpb: 交叉概率
        mutpb: 变异概率
        ngen: 进化代数
        headway_range: 车头时距范围
        stats: DEAP统计对象
        halloffame: DEAP名人堂对象
        parameters: 自定义参数
        global_demand_data: 全局需求数据
        verbose: 是否打印详细信息

    Returns:
        tuple: (final_population, logbook)
    """
    if verbose:
        print("=== 开始运行遗传算法 ===")
        print(f"种群大小: {population_size}")
        print(f"车辆数量: {num_vehicles}")
        print(f"最大模块数: {max_modules}")
        print(f"车头时距范围: {headway_range}")
        print(f"交叉概率: {cxpb}")
        print(f"变异概率: {mutpb}")
        print(f"进化代数: {ngen}")

    # 生成初始种群
    if verbose:
        print("\n--- 进入遗传算法 步骤1: 生成初始种群 ---")

    population = []
    for i in range(population_size):
        individual = toolbox.individual()
        population.append(individual)
        # if verbose and (i + 1) % 10 == 0:
        #     print(f"已初始化 {i + 1}/{population_size} 个个体")
        print(f"已初始化 {i + 1}/{population_size} 个个体")

    if verbose:
        print(f"种群初始化完成，共 {len(population)} 个个体")

    # 运行遗传算法
    if verbose:
        print("\n--- 进入遗传算法 步骤2: 运行遗传算法 ---")

    final_population, logbook, cost_history = customized_genetic_algorithm(
        population=population,
        toolbox=toolbox,
        cxpb=cxpb,
        mutpb=mutpb,
        ngen=ngen,
        stats=stats,
        halloffame=halloffame,
        parameters=parameters,
        global_demand_data=global_demand_data,
        verbose=verbose
    )

    if verbose:
        print("\n=== 遗传算法运行完成 ===")

    return final_population, logbook, cost_history