import streamlit as st
import random

# 角色系统：SP系统平衡版
chars = {
    "Shaw Zer": {"hp": 150, "atk": 15, "desc": "🐰 傲娇男娘", "skill": "【撒娇】：回 40HP (消耗 25SP)", "buff": "【嘴硬】：下回合防御加倍 (消耗 67SP)"},
    "Zhi Wei": {"hp": 130, "atk": 25, "desc": "👁️ 雷达官", "skill": "【扫描】：对方扣 30HP (消耗 25SP)", "buff": "【预判】：下回合攻击翻倍 (消耗 67SP)"},
    "Qi Yu": {"hp": 200, "atk": 12, "desc": "🍹 冰水仙人", "skill": "【Teh O Ais】：回 50HP (消耗 25SP)", "buff": "【静止】：减少对方 50SP (消耗 67SP)"},
    "Jun Zi": {"hp": 110, "atk": 35, "desc": "🐶 哈士奇", "skill": "【撕咬】：造成 40HP 伤害 (消耗 25SP)", "buff": "【狂暴】：全属性大幅提升 (消耗 67SP)"},
    "Keith Goh": {"hp": 170, "atk": 20, "desc": "👴 暴走老御宅", "skill": "【动漫吐槽】：造成 35HP 伤害 (消耗 25SP)", "buff": "【结界】：全员无效化 1 回合 (消耗 67SP)"}
}

st.title("⚔️ 隆中华：SP 策略巅峰赛")

if 'g' not in st.session_state:
    st.session_state.g = {'started': False}

if not st.session_state.g['started']:
    p = st.selectbox("选你的角色:", list(chars.keys()))
    if st.button("开始"):
        st.session_state.g = {'started': True, 'p': p, 'o': random.choice([c for c in chars if c != p]),
                              'p_hp': chars[p]['hp'], 'o_hp': chars[random.choice([c for c in chars if c != p])]['hp'],
                              'p_sp': 40, 'log': ["开始！"]}
        st.rerun()
else:
    p, o = st.session_state.g['p'], st.session_state.g['o']
    st.metric("你的 SP", st.session_state.g['p_sp'], delta=10) # 每回合回10
    c1, c2 = st.columns(2)
    c1.metric("你的 HP", st.session_state.g['p_hp'])
    c2.metric("对手 HP", st.session_state.g['o_hp'])

    action = st.radio("指令 (上限100SP):", ["普通攻击 (5SP)", "技能 (25SP)", "强化 (67SP)", "大招 (78SP)"])
    if st.button("出招"):
        sp_costs = {"普通攻击 (5SP)": 5, "技能 (25SP)": 25, "强化 (67SP)": 67, "大招 (78SP)": 78}
        cost = sp_costs[action]
        
        if st.session_state.g['p_sp'] < cost:
            st.error("SP不足！")
        else:
            st.session_state.g['p_sp'] = min(100, st.session_state.g['p_sp'] - cost + 10) # 扣费后加10点回复
            
            # 伤害逻辑
            if "普通" in action: st.session_state.g['o_hp'] -= chars[p]['atk']
            elif "技能" in action: st.session_state.g['o_hp'] -= 30
            elif "强化" in action: st.session_state.g['p_hp'] += 20 # 强化加buff
            elif "大招" in action: st.session_state.g['o_hp'] -= 60
            
            # 对手行动
            st.session_state.g['p_hp'] -= 15
            st.rerun()

    if st.session_state.g['p_hp'] <= 0: st.error("你输了！"); st.session_state.g['started'] = False
