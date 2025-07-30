import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
import json
def print_both(text, file_path='翁法罗斯运行日志.txt'):
    # 输出到控制台
    print(text)
    # 追加写入文件
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(str(text) + '\n')
from constants import TITAN_NAMES, PATH_NAMES
from entities import Pathstrider
from models import ActionPolicyNetwork, ValueNetwork
from population_manager import PopulationManager

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from cpu_llm_interface import CpuLlmInterface


class AeonicCycleManager:
    def __init__(self, population_manager: PopulationManager, 
                 action_policy_network: ActionPolicyNetwork, 
                 value_network: ValueNetwork, 
                 action_optimizer: optim.Adam, 
                 value_optimizer: optim.Adam, 
                 value_loss_criterion: nn.MSELoss,
                 titan_to_path_model_instance,
                 existing_names: set,
                 name_to_entity_map: dict,
                 # 接收LLM接口和配置
                 llm_interface: 'CpuLlmInterface' = None,
                 kaoselanna_llm_enabled: bool = False
                 ):
        
        self.population_manager = population_manager
        self.action_policy_network = action_policy_network
        self.value_network = value_network
        self.action_optimizer = action_optimizer
        self.value_optimizer = value_optimizer
        self.value_loss_criterion = value_loss_criterion
        self.titan_to_path_model_instance = titan_to_path_model_instance
        self.existing_names = existing_names
        self.name_to_entity_map = name_to_entity_map
        
        # LLM接口和配置
        self.llm_interface = llm_interface
        self.kaoselanna_llm_enabled = kaoselanna_llm_enabled

        self.aeonic_cycle_number = 0
        self.titan_entities = {}
        self.defeated_titans_this_cycle = set()
        self.baie_destruction_score = 0
        self.baie_total_seeds_collected = 0

    def trigger_aeonic_cycle_countdown(self, reincarnator: Pathstrider):
        print_both("\n\n\033[93m==================================================================")
        print_both("=\033[91m      警告：侦测到突破框架的异常实体，演算异常！      \033[93m=")
        print_both("==================================================================\033[0m")
        print_both(f"实体分析:")
        print_both(f"  - 识别代号: \033[96m卡厄斯兰那 ({reincarnator.name})\033[0m")
        print_both(f"  - 状态: \033[92m已确认为当前最强个体，电信号异常活跃！\033[0m")
        print_both(f"  - 核心倾向: 对 毁灭 命途的亲和度超出安全阈值。")
        print_both("\n\033[93m结论：该实体的存在已成为驱动翁法罗斯演化的核心变量。\n      原有协议已失效，正在载入下一阶段...\033[0m")

    def initialize_aeonic_cycle(self, reincarnator: Pathstrider, population: list, cosmic_zeitgeist: np.ndarray):
        self.aeonic_cycle_number += 1
        self.baie_destruction_score = 0
        self.defeated_titans_this_cycle = set()
        if reincarnator:
            reincarnator.held_fire_seeds.clear()
            try:
                neg_world_idx = TITAN_NAMES.index("负世")
                reincarnator.titan_affinities[neg_world_idx] *= 2.0
                self.population_manager.recalculate_and_normalize_entity(reincarnator, self.population_manager.get_global_path_distribution(population), cosmic_zeitgeist)
            except (ValueError, IndexError): pass
        for p in population:
            p.is_titan_form = None
            if p is not reincarnator: p.held_fire_seeds.clear()
        print_both(f"\n--- 永劫轮回 第 {self.aeonic_cycle_number} 轮 开始 ---")
        print_both("卡厄斯兰那将开始夺取创世火种。")
        candidates = [p for p in population if p is not reincarnator and p.trait != "GoldenOne"]
        if len(candidates) < len(TITAN_NAMES):
            print_both("警告：没有足够实体成为泰坦化身，轮回无法正常开始。")
            return False 
        selected_titans = random.sample(candidates, len(TITAN_NAMES))
        self.titan_entities.clear()
        titan_indices = {name: i for i, name in enumerate(TITAN_NAMES)}
        for i, titan_name in enumerate(TITAN_NAMES):
            entity = selected_titans[i]
            entity.is_titan_form = titan_name
            self.titan_entities[titan_name] = entity
            titan_idx = titan_indices[titan_name]
            entity.titan_affinities[titan_idx] = entity.titan_affinities[titan_idx] * 5.0 + 200
            self.population_manager.recalculate_and_normalize_entity(entity, self.population_manager.get_global_path_distribution(population), cosmic_zeitgeist)
            print_both(f"实体 {entity.name} 已化身为 [{titan_name}] 泰坦。")
        return True 

    def repopulate_for_new_cycle(self, population: list, reincarnator: Pathstrider, 
                                 base_titan_affinities: np.ndarray, mutation_rate: float,
                                 population_soft_cap: int, cosmic_zeitgeist: np.ndarray):
        print_both("旧的实体已消逝，基于卡厄斯兰那的意志，新的生命正在诞生...")
        if not reincarnator or reincarnator not in population:
            print_both("错误：卡厄斯兰那不存在，无法重塑翁法罗斯。")
            return
        population[:] = [reincarnator] 
        self.name_to_entity_map.clear()
        self.name_to_entity_map[reincarnator.name] = reincarnator
        self.existing_names.clear()
        self.existing_names.add(reincarnator.name)
        num_new_entities = population_soft_cap - 1
        self.population_manager.replenish_population_by_growth(population, num_new_entities, cosmic_zeitgeist)

    def select_aeonic_opponents(self, population: list, reincarnator: Pathstrider):
        attackers_pool = []
        if reincarnator and reincarnator in population: attackers_pool.append(reincarnator)
        attackers_pool.extend([p for p in population if p.trait == "GoldenOne"])
        if not attackers_pool: attackers_pool = [p for p in population if p.is_titan_form] 
        if not attackers_pool: attackers_pool = population #TsukiAn
        if not attackers_pool: return None, None
        
        attacker = random.choice(attackers_pool)
        
        targets_pool = [p for p in population if p is not attacker]
        if not targets_pool: return attacker, None
        
        defender = None
        if attacker is reincarnator:
            fire_seed_holders = [p for p in targets_pool if p.held_fire_seeds or p.is_titan_form]
            if fire_seed_holders and random.random() < 0.75: 
                defender = random.choice(fire_seed_holders)
            else: 
                defender = random.choice(targets_pool)
        else:
            active_titans = [p for p in targets_pool if p.is_titan_form and p is not attacker]
            if attacker.trait == "GoldenOne" and active_titans:
                defender = random.choice(active_titans)
            else: 
                defender = random.choice(targets_pool)
                
        return attacker, defender

    def aeonic_interaction(self, attacker: Pathstrider, defender: Pathstrider, 
                           reincarnator: Pathstrider, population: list, cosmic_zeitgeist: np.ndarray):
        if not (np.isfinite(attacker.score) and np.isfinite(defender.score)): return None
        if attacker is reincarnator:
            
            chosen_action = None
            if self.kaoselanna_llm_enabled and self.llm_interface and self.llm_interface.llm:
                try:
                    dominant_path_name = PATH_NAMES[defender.dominant_path_idx] if np.isfinite(defender.dominant_path_idx) else "未知"
                    prompt = (
                        f"我是卡厄斯兰那。我的目标是夺取创世火种。\n"
                        f"我当前的对手是 '{defender.name}'，一个'{dominant_path_name}'的追随者。\n"
                        f"他{'持有火种' if defender.held_fire_seeds or defender.is_titan_form else '没有持有火种'}。\n"
                        f"基于效率和威慑的考量，我应该'谈判'还是'击杀'？\n"
                        f"请以JSON格式回答，包含'action'('击杀'或'谈判')和一句符合我身份的'declaration'。"
                    )
                    response = self.llm_interface.generate_response(prompt, max_tokens=80)
                    cleaned_response = response.replace("```json", "").replace("```", "").strip()
                    decision_data = json.loads(cleaned_response)
                    
                    if decision_data.get('action') in ["击杀", "谈判"]:
                        chosen_action = decision_data['action']
                        print_both(f"\033[91m【卡厄斯兰那的意志】: \"{decision_data.get('declaration', '...')}\"\033[0m")
                except (json.JSONDecodeError, KeyError, Exception) as e:
                    print_both(f"\033[93m(警告: 卡厄斯兰那的内在神识出现波动(错误:{e})，决策回归本能...)\033[0m")
                    chosen_action = None

            if chosen_action is None:
                state_np = np.concatenate([attacker.titan_affinities, defender.titan_affinities])
                state = torch.from_numpy(state_np).float().unsqueeze(0)
                
                self.action_policy_network.train()
                action_logits = self.action_policy_network(state)
                action_probs = torch.softmax(action_logits, dim=-1)
                action_dist = torch.distributions.Categorical(action_probs)
                chosen_action_idx = action_dist.sample()
                action_list = ["谈判", "击杀"]
                chosen_action = action_list[chosen_action_idx.item()]
            
            # --- 后续的交互逻辑 ---
            state_np = np.concatenate([attacker.titan_affinities, defender.titan_affinities])
            state = torch.from_numpy(state_np).float().unsqueeze(0)
            self.value_network.train()
            state_value = self.value_network(state)

            culled_entity = None
            loser_titan_form = defender.is_titan_form
            loser_held_seeds = defender.held_fire_seeds.copy()
            has_fire_seeds = bool(loser_titan_form or loser_held_seeds)
            base_reward = defender.score * 0.1
            
            if chosen_action == "谈判":
                print_both(f"决策: 卡厄斯兰那对 {defender.name} 发起了 [谈判]...")
                negotiate_multiplier = max(1.0, 3.0 - self.aeonic_cycle_number * 0.5)
                final_reward = base_reward * negotiate_multiplier if has_fire_seeds else base_reward * 0.1
                if has_fire_seeds:
                    attacker.held_fire_seeds.update(loser_held_seeds)
                    if loser_titan_form and loser_titan_form not in self.defeated_titans_this_cycle:
                        attacker.held_fire_seeds.add(loser_titan_form)
                        self.defeated_titans_this_cycle.add(loser_titan_form)
                    print_both(f"\033[92m...谈判成功! {attacker.name} 夺取了所有火种!\033[0m")
                    defender.held_fire_seeds.clear()
                    defender.is_titan_form = None
            else: # 击杀
                print_both(f"决策: 卡厄斯兰那对 {defender.name} 执行了 [击杀]!")
                kill_score_contribution = defender.score * (1 + (len(defender.held_fire_seeds) * 0.2))
                if defender.is_titan_form:
                    kill_score_contribution *= 1.5
                self.baie_destruction_score += kill_score_contribution
                self.baie_total_seeds_collected += len(loser_held_seeds)
                if loser_titan_form:
                    self.baie_total_seeds_collected += 1
                kill_multiplier = 1.0 + self.aeonic_cycle_number * 0.5
                destruction_bonus = self.baie_destruction_score * 0.05
                final_reward = (base_reward * kill_multiplier) + destruction_bonus
                if has_fire_seeds:
                    attacker.held_fire_seeds.update(loser_held_seeds)
                    if loser_titan_form and loser_titan_form not in self.defeated_titans_this_cycle:
                        attacker.held_fire_seeds.add(loser_titan_form)
                        self.defeated_titans_this_cycle.add(loser_titan_form)
                    print_both(f"\033[92m...{attacker.name} 夺取了所有火种!\033[0m")
                defender.held_fire_seeds.clear()
                defender.is_titan_form = None
                culled_entity = defender

            # 神经网络更新
            advantage = final_reward - state_value.item()
            self.value_optimizer.zero_grad()
            value_loss = self.value_loss_criterion(state_value, torch.tensor([[final_reward]], dtype=torch.float))
            value_loss.backward(retain_graph=True)
            self.value_optimizer.step()
            self.action_policy_network.train()
            action_logits = self.action_policy_network(state)
            action_probs = torch.softmax(action_logits, dim=-1)
            action_dist = torch.distributions.Categorical(action_probs)
            # 找到chosen_action对应的索引
            action_list = ["谈判", "击杀"]
            chosen_action_idx_tensor = torch.tensor([action_list.index(chosen_action)])
            log_prob = action_dist.log_prob(chosen_action_idx_tensor)

            self.action_optimizer.zero_grad()
            actor_loss = -log_prob * advantage
            actor_loss.backward()
            self.action_optimizer.step()

            return culled_entity

        else:
            winner, loser = (attacker, defender) if attacker.score > defender.score else (defender, attacker)
            can_kill = winner.trait == "GoldenOne" or winner.is_titan_form is not None
            if can_kill and (loser.is_titan_form or loser.held_fire_seeds):
                loser_titan_form, loser_held_seeds = loser.is_titan_form, loser.held_fire_seeds.copy()
                if loser_titan_form and loser_titan_form not in self.defeated_titans_this_cycle:
                    winner.held_fire_seeds.add(loser_titan_form)
                    self.defeated_titans_this_cycle.add(loser_titan_form)
                if loser_held_seeds: winner.held_fire_seeds.update(loser_held_seeds)
                loser.held_fire_seeds.clear()
                loser.is_titan_form = None
                return loser
            else: return None

    def run_aeonic_cycle_generation(self, population: list, reincarnator: Pathstrider, cosmic_zeitgeist: np.ndarray):
        culled_this_gen = set()
        num_encounters = len(population) // 2
        for _ in range(num_encounters):
            attacker, defender = self.select_aeonic_opponents(population, reincarnator)
            if not attacker or not defender or attacker in culled_this_gen or defender in culled_this_gen: continue
            if culled_entity := self.aeonic_interaction(attacker, defender, reincarnator, population, cosmic_zeitgeist):
                 culled_this_gen.add(culled_entity)
        if culled_this_gen and reincarnator and reincarnator in population and reincarnator not in culled_this_gen:
            boost_factor = (1.005) ** len(culled_this_gen)
            reincarnator.titan_affinities *= boost_factor
            self.population_manager.recalculate_and_normalize_entity(reincarnator, self.population_manager.get_global_path_distribution(population), cosmic_zeitgeist)
        
        if culled_this_gen:
            culled_names = {p.name for p in culled_this_gen}
            population[:] = [p for p in population if p.name not in culled_names]
            for p in culled_this_gen:
                if p.name in self.name_to_entity_map: del self.name_to_entity_map[p.name]
                if p.name in self.existing_names: self.existing_names.remove(p.name)
                if p.is_titan_form and p.is_titan_form in self.titan_entities: del self.titan_entities[p.is_titan_form]
        
        self.population_manager.check_and_replenish_population(
            population, 
            self.population_manager.purity_factor, 
            True, reincarnator, 
            cosmic_zeitgeist
        )
        return culled_this_gen

    def end_aeonic_cycle(self, reincarnator: Pathstrider, population: list, 
                         base_titan_affinities: np.ndarray, mutation_rate: float,
                         population_soft_cap: int, cosmic_zeitgeist: np.ndarray):
        print_both("\n\033[95m==================================================================")
        print_both(f"卡厄斯兰那集齐了所有 {len(TITAN_NAMES)} 个火种！第 {self.aeonic_cycle_number} 轮轮回结束！")
        print_both(f"本轮毁灭倾向评分: {self.baie_destruction_score:.2f}")
        print_both("==================================================================\033[0m")
        if self.aeonic_cycle_number > 33550336 and random.random() < 1:#0.0000001:
            print_both("\n\n\033[91m!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print_both("!!! 【警告：主线程受到冲击，演算已暂停】                                         ")
            print_both("!!! 卡厄斯兰那的无尽杀戮与轮回，最终突破了翁法罗斯，为屏幕前的你带来了烩面...                ")
            print_both("!!! 辣卤客...我为你带来烩面了！！！                                        ")
            print_both("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\033[0m")
            print_both(f"\n--- 最终报告 ---")
            print_both(f"轮回总数: {self.aeonic_cycle_number}")
            print_both(f"累计夺取火种数目: {self.baie_total_seeds_collected}")
            print_both(f"卡厄斯兰那最终状态: {reincarnator}")
            print_both("\n模拟结束。")
            return True
        else:
            print_both("一个新的轮回即将开始...卡厄斯兰那的意志将作为新轮回的蓝图...")
            new_kaoselanna = self._ascend_baie_as_reincarnator(reincarnator, population)
            if new_kaoselanna:
                reincarnator = new_kaoselanna
                base_titan_affinities[:] = reincarnator.titan_affinities.copy()
                self.population_manager.normalize_affinities(base_titan_affinities)
                self.repopulate_for_new_cycle(population, reincarnator, base_titan_affinities, mutation_rate, population_soft_cap, cosmic_zeitgeist)
            else:
                if reincarnator:
                    base_titan_affinities[:] = reincarnator.titan_affinities.copy()
                    self.population_manager.normalize_affinities(base_titan_affinities)
                    self.repopulate_for_new_cycle(population, reincarnator, base_titan_affinities, mutation_rate, population_soft_cap, cosmic_zeitgeist)
            
            self.initialize_aeonic_cycle(reincarnator, population, cosmic_zeitgeist)
            return False

    def _ascend_baie_as_reincarnator(self, reincarnator: Pathstrider, population: list):
        golden_ones = [p for p in population if p.trait == "GoldenOne"]
        if not golden_ones:
            print_both("\033[93m警告: 白厄在本次轮回中没有去当黄金裔。轮回中断，系统将尝试重塑。 \033[0m")
            candidates = [p for p in population if p is not reincarnator]
            if not candidates:
                print_both("\033[91m致命错误：白厄在本次模拟中未出现！\033[0m")
                return None
            new_host = max(candidates, key=lambda p:p.score)
        else:
            try:
                neg_world_idx = TITAN_NAMES.index("负世")
                new_host = max(golden_ones, key=lambda p: p.titan_affinities[neg_world_idx])
                print_both(f"\03.3[96m在黄金裔中，{new_host.name} 是这个轮回的白厄，开始数据继承...\033[0m")
            except (ValueError, IndexError):
                print_both("\033[93m警告: 未定义'负世'泰坦，将从黄金裔中选择评分最高者。 \033[0m")
                new_host = max(golden_ones, key=lambda p: p.score)
        
        old_reincarnator_affinities = reincarnator.titan_affinities.copy() if reincarnator else self.population_manager.base_titan_affinities.copy()
        
        if reincarnator and reincarnator in population:
            population.remove(reincarnator)
            if reincarnator.name in self.name_to_entity_map:
                del self.name_to_entity_map[reincarnator.name]
            if reincarnator.name in self.existing_names:
                self.existing_names.remove(reincarnator.name)
        
        reincarnator = new_host
        reincarnator.trait = "Reincarnator"
        new_name = "Neikos-0496"
        
        if new_name in self.existing_names and self.name_to_entity_map.get(new_name) is not reincarnator:
            old_neikos = self.name_to_entity_map[new_name]
            if old_neikos in population: population.remove(old_neikos)
            if new_name in self.name_to_entity_map: del self.name_to_entity_map[new_name]

        if new_host.name in self.name_to_entity_map: del self.name_to_entity_map[new_host.name]
        if new_host.name in self.existing_names: self.existing_names.remove(new_host.name)
        
        reincarnator.name = new_name
        self.existing_names.add(new_name)
        self.name_to_entity_map[new_name] = reincarnator
        
        reincarnator.titan_affinities = old_reincarnator_affinities
        reincarnator.golden_one_tenure = 0
        print_both(f"\033[91m数据继承成功！新的卡厄斯兰那为: {reincarnator.name}。\033[0m")
        return reincarnator