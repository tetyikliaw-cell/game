import streamlit as st
import random

# 角色系统：完整技能与描述
chars = {
    "Shaw Zer": {"hp": 150, "atk": 15, "skill_name": "撒娇求带", "ult_name": "极限嘴硬"},
    "Zhi Wei": {"hp": 130, "atk": 25, "skill_name": "雷达扫描", "ult_name": "学弟捕捉"},
    "Qi Yu": {"hp": 200, "atk": 12, "skill_name": "Teh O Ais补给", "ult_name": "虚无入定"},
    "Jun Zi": {"hp": 110, "atk": 35, "skill_name": "哈士奇撕咬", "ult_name": "狂暴觉醒"},
    "Keith Goh": {"hp": 170, "atk": 20, "skill_name": "动漫吐槽", "ult_name": "二次元审判"}
}

st.title("⚔️ 隆中华：嘴硬争霸赛")

if 'g' not in st.session_state:
    st.session_state.g = {'started': False}

if not st.session_state.g['started']:
    p = st.selectbox("选择你的角色:", list(chars.keys()))
    if st.button("开始挑战"):
        o = random.choice([c for c in chars if c != p])
        st.session_state.g = {'started': True, 'p': p, 'o': o, 'p_hp': chars[p]['hp'], 
                              'o_hp': chars[o]['hp'], 'p_sp': 40, 'turn': 1, 'log': ["战斗开始！"]}
        st.rerun()
else:
    g = st.session_state.g
    st.subheader(f"第 {g['turn']} 回合 | 你 vs {g['o']}")
    
    col1, col2 = st.columns(2)
    col1.metric("你的 HP", g['p_hp'])
    col2.metric("对手 HP", g['o_hp'])
    st.progress(g['p_sp']/100, text=f"SP点数: {g['p_sp']}/100")

    # 指令区
    action = st.radio("选择战术:", [f"普通攻击 (5SP)", f"{chars[g['p']]['skill_name']} (25SP)", f"大招: {chars[g['p']]['ult_name']} (78SP)"])
    
    if st.button("确认出招"):
        costs = {"普通攻击 (5SP)": 5, chars[g['p']]['skill_name']: 25, chars[g['p']]['ult_name']: 78}
        # 这里动态匹配指令
        cost = 5 if "普通" in action else (25 if "技能" not in action else 78)
        
        if g['p_sp'] < cost:
            st.error("SP不足，先普通攻击积攒点数吧！")
        else:
            g['p_sp'] = min(100, g['p_sp'] - cost + 10)
            # 战斗结算
            dmg = chars[g['p']]['atk'] + (20 if "大招" in action else 0)
            g['o_hp'] -= dmg
            g['log'].append(f"第{g['turn']}回合: 你使用了 {action}，造成 {dmg} 点伤害！")
            
            # 对手行动
            o_dmg = chars[g['o']]['atk']
            g['p_hp'] -= o_dmg
            g['log'].append(f"对手 {g['o']} 反击，造成 {o_dmg} 点伤害！")
            g['turn'] += 1
            st.rerun()

    st.write("---")
    st.write("### 战斗日志")
    for l in reversed(g['log'][-3:]): st.write(l)
    
    if g['p_hp'] <= 0: st.error("你破防了，明天上课被罚站！"); g['started'] = False
    elif g['o_hp'] <= 0: st.success("你赢了，全班请你喝 Teh O Ais！"); g['started'] = False
