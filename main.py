# main.py

import os
import sys
import traceback
import colorama
from simulation import AeonEvolution
def print_both(text, file_path='翁法罗斯运行日志.txt'):
    # 输出到控制台
    print(text)
    # 追加写入文件
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(str(text) + '\n')
def run_simple():
    """ 以简单的控制台模式运行模拟 """
    colorama.init()  # 初始化 colorama 以在 Windows 上启用 ANSI 颜色代码
    sim = None
    try:
        sim = AeonEvolution(
            # --- LLM 控制 ---
            bard_frequency=0,         
            laertes_frequency=0,      
            kaoselanna_llm_enabled=False,

            # --- 其他模拟参数 ---
            num_initial_entities=200, 
            golden_one_cap=12, 
            population_soft_cap=300,
            population_hard_cap=500, 
            growth_factor=0.35, 
            mutation_rate=0.25,
            culling_strength=0.85, 
            encounter_similarity=0.35, 
            purity_factor=0.01,
            initial_rl_lr=0.005, 
            golden_one_reversion_prob=0.1,
            elite_selection_percentile=80, 
            aeonic_event_prob=0.05,
            initial_max_affinity_norm=10000.0, 
            target_avg_score=50.0,
            norm_adjustment_strength=0.05
        )
        print_both("=== 翁法罗斯 v10.3 (Dev) 启动 ===")
        sim.start(num_generations=33550336)

    except KeyboardInterrupt:
        print_both("\n\n模拟被用户中断。正在退出...")
        # sys.exit(0) 

    except Exception:
        # 在发生其他异常时打印完整的追溯信息
        traceback.print_exc()

    finally:
        # 确保在模拟结束或中断时保存模型
        if sim and hasattr(sim, 'policy_saver'):
            print_both("\n正在尝试保存策略模型...")
            sim.policy_saver.save_policy_models()
        
        print("\n模拟已结束。按任意键退出。")
        if os.name == 'nt':
            os.system('pause')
        sys.exit(0) 


if __name__ == "__main__":
    run_simple()