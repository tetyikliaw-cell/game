import streamlit as st
import random

# 角色数据
chars = {
    "Shaw Zer": {"hp": 150, "atk": 15, "skill": "撒娇求带", "buff": "极限嘴硬", "ult": "掉星暴走"},
    "Zhi Wei": {"hp": 130, "atk": 25, "skill": "雷达扫描", "buff": "学弟捕捉", "ult": "雷达过载"},
    "Qi Yu": {"hp": 200, "atk": 12, "skill": "Teh O Ais补给", "buff": "虚无入定", "ult": "冰封宇宙"},
    "Jun Zi": {"hp": 110, "atk": 35, "skill": "哈士奇撕咬", "buff": "狂暴觉醒", "ult": "哈士奇陨石"},
    "Keith Goh": {"hp": 170, "atk": 20, "skill": "动漫吐槽", "buff": "二次元结界", "ult": "老宅男的审判"},
    "德育月": {"hp": 250, "atk": 0, "skill": "魔王降临", "buff": "规则修改", "ult": "终极处刑", "is_boss": True}
}

# 嘲讽库
taunts = ["笑死，你会玩吗？", "隆中华没人了吗？", "太弱了，换个姿势再来！", "这是你最强的招？", "就这？"]

st.title(" 隆中华：大乱斗 ")

if 'started' not in st.session_state:
    st.session_state.update({'started': False, 'log': []})

if not st.session_state.started:
    if st.button("开始抽卡决斗"):
        pool = list(chars.keys())
        weights = [9.1 if c == "德育月" else (90.9/5) for c in pool]
        p = random.choices(pool, weights=weights)[0]
        o = random.choices(pool, weights=weights)[0]
        while o == p: o = random.choices(pool, weights=weights)[0]
        
        is_p_boss = chars[p].get('is_boss', False)
        st.session_state.update({
            'started': True, 'p': p, 'o': o, 'p_hp': chars[p]['hp'], 'o_hp': chars[o]['hp'],
            'sp': 100 if is_p_boss else 40, 'max_sp': 150 if is_p_boss else 100,
            'turn': 1, 'log': [f"决斗开始：{p} vs {o}"]
        })
        st.rerun()
else:
    p_data = chars[st.session_state.p]
    is_p_boss = p_data.get('is_boss', False)
    
    st.subheader(f"第 {st.session_state.turn} 回合 | {st.session_state.p} vs {st.session_state.o}")
    col1, col2 = st.columns(2)
    col1.metric("你的 HP", max(0, st.session_state.p_hp))
    col2.metric("对手 HP", max(0, st.session_state.o_hp))
    st.progress(st.session_state.sp / st.session_state.max_sp, text=f"SP: {st.session_state.sp}/{st.session_state.max_sp}")

    if st.session_state.p_hp > 0 and st.session_state.o_hp > 0:
        costs = {"普通攻击": 5, "技能": 25, "强化": 67, "大招": 78}
        options = [f"技能: {p_data['skill']} (25SP)", f"强化: {p_data['buff']} (67SP)", f"大招: {p_data['ult']} (78SP)"]
        if not is_p_boss: options.insert(0, "普通攻击 (5SP)")
        action = st.radio("选择指令:", options)
        
        if st.button("执行回合"):
            chosen_cost = 5 if "普通" in action else (25 if "技能" in action else (67 if "强化" in action else 78))
            
            if st.session_state.sp < chosen_cost:
                st.error(f"⚠️ SP 不足！需要 {chosen_cost} SP。")
            else:
                # 触发暴击 (20% 概率)
                is_crit = random.random() < 0.2
                # 计算伤害
                if is_p_boss:
                    dmg = 35 if "技能" in action else (45 if "强化" in action else 91)
                else:
                    base_dmg = 15 if "普通" in action else (p_data['atk'] + 10)
                    dmg = base_dmg * 2 if is_crit else base_dmg
                
                # 更新状态
                st.session_state.sp -= chosen_cost
                st.session_state.o_hp = max(0, st.session_state.o_hp - dmg)
                st.session_state.sp = min(st.session_state.max_sp, st.session_state.sp + 10)
                
                # 记录日志与嘲讽
                crit_text = "【暴击！】" if is_crit else ""
                taunt = random.choice(taunts)
                st.session_state.log.append(f"{crit_text}使用了 {action.split(':')[0]}，造成 {dmg} 点伤害。对手反击：{taunt}")
                
                if st.session_state.o_hp <= 0:
                    st.session_state.log.append("🎉 对手当场暴毙！"); st.balloons()
                else:
                    st.session_state.p_hp -= 15
                    st.session_state.log.append("对手反击造成 15 点伤害。")
                st.session_state.turn += 1
                st.rerun()
    else:
        if st.button("再来一局"): st.session_state.started = False; st.rerun()

    st.write("### 战斗日志")
    for l in reversed(st.session_state.log[-5:]): st.write(l)
