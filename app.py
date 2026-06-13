import streamlit as st
import random

# 角色数据：德育月现在和大家平起平坐，但带有 BOSS 属性
chars = {
    "Shaw Zer": {"hp": 150, "atk": 15, "skill": "撒娇求带", "buff": "极限嘴硬", "ult": "掉星暴走"},
    "Zhi Wei": {"hp": 130, "atk": 25, "skill": "雷达扫描", "buff": "学弟捕捉", "ult": "雷达过载"},
    "Qi Yu": {"hp": 200, "atk": 12, "skill": "Teh O Ais补给", "buff": "虚无入定", "ult": "冰封宇宙"},
    "Jun Zi": {"hp": 110, "atk": 35, "skill": "哈士奇撕咬", "buff": "狂暴觉醒", "ult": "哈士奇陨石"},
    "Keith Goh": {"hp": 170, "atk": 20, "skill": "动漫吐槽", "buff": "二次元结界", "ult": "老宅男的审判"},
    "德育月": {"hp": 250, "atk": 0, "skill": "魔王降临", "buff": "规则修改", "ult": "终极处刑", "is_boss": True}
}

st.title("🃏 隆中华：智障抽卡大乱斗 v7.1 (全员BOSS版)")

if 'started' not in st.session_state:
    st.session_state.update({'started': False, 'log': []})

if not st.session_state.started:
    if st.button("开始抽卡决斗"):
        pool = list(chars.keys())
        # 统一权重：德育月概率 9.1%
        weights = [18.18 if c != "德育月" else 9.1 for c in pool]
        
        p = random.choices(pool, weights=weights)[0]
        # 对手也从这个池子里抽，所以对手也可能抽到德育月
        o = random.choices(pool, weights=weights)[0]
        while o == p: # 确保不会抽到一样的人
            o = random.choices(pool, weights=weights)[0]
        
        st.session_state.update({
            'started': True, 'p': p, 'o': o, 'p_hp': chars[p]['hp'], 'o_hp': chars[o]['hp'],
            'sp': 100 if chars[p].get('is_boss') else 40, 
            'max_sp': 150 if chars[p].get('is_boss') else 100,
            'turn': 1, 'log': [f"决斗开始！你 ({p}) vs 对手 ({o})"]
        })
        st.rerun()
else:
    # 战斗逻辑保持不变，但支持 BOSS 属性的自动判定
    p_data = chars[st.session_state.p]
    st.subheader(f"第 {st.session_state.turn} 回合 | {st.session_state.p} vs {st.session_state.o}")
    col1, col2 = st.columns(2)
    col1.metric("你的 HP", max(0, st.session_state.p_hp))
    col2.metric("对手 HP", max(0, st.session_state.o_hp))
    st.progress(st.session_state.sp/st.session_state.max_sp, text=f"SP: {st.session_state.sp}/{st.session_state.max_sp}")

    if st.session_state.p_hp > 0 and st.session_state.o_hp > 0:
        options = [f"技能: {p_data['skill']} (25SP)", f"强化: {p_data['buff']} (67SP)", f"大招: {p_data['ult']} (78SP)"]
        if not p_data.get('is_boss'): options.insert(0, "普通攻击 (5SP)")
        action = st.radio("选择指令:", options)
        
        if st.button("执行回合"):
            if "普通" in action: dmg = 15
            elif "技能" in action: dmg = 35 if p_data.get('is_boss') else 25
            elif "强化" in action: dmg = 45 if p_data.get('is_boss') else 35
            else: dmg = 91 if p_data.get('is_boss') else 60
            
            st.session_state.o_hp = max(0, st.session_state.o_hp - dmg)
            st.session_state.sp = min(st.session_state.max_sp, st.session_state.sp + 10)
            
            if st.session_state.o_hp <= 0:
                st.session_state.log.append("🎉 战斗结束！"); st.balloons()
            else:
                st.session_state.p_hp = max(0, st.session_state.p_hp - 20)
                st.session_state.log.append(f"回合结束，双方换血伤害 20。")
            st.session_state.turn += 1
            st.rerun()
    else:
        if st.button("再来一局"): st.session_state.started = False; st.rerun()
