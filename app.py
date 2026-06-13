import streamlit as st
import random

# 角色数据
chars = {
    "Shaw Zer": {"hp": 150, "atk": 15, "skill": "撒娇求带", "buff": "极限嘴硬", "ult": "掉星暴走"},
    "Zhi Wei": {"hp": 130, "atk": 25, "skill": "雷达扫描", "buff": "学弟捕捉", "ult": "雷达过载"},
    "Qi Yu": {"hp": 200, "atk": 12, "skill": "Teh O Ais补给", "buff": "虚无入定", "ult": "冰封宇宙"},
    "Jun Zi": {"hp": 110, "atk": 35, "skill": "哈士奇撕咬", "buff": "狂暴觉醒", "ult": "哈士奇陨石"},
    "Keith Goh": {"hp": 170, "atk": 20, "skill": "动漫吐槽", "buff": "二次元结界", "ult": "老宅男的审判"}
}

st.title("⚔️ 隆中华：嘴硬争霸赛 v3.1")

if 'started' not in st.session_state:
    st.session_state.update({'started': False, 'log': []})

if not st.session_state.started:
    p = st.selectbox("选你的角色:", list(chars.keys()))
    if st.button("开始挑战"):
        o = random.choice([c for c in chars if c != p])
        st.session_state.update({'started': True, 'p': p, 'o': o, 'p_hp': chars[p]['hp'], 
                                 'o_hp': chars[o]['hp'], 'sp': 40, 'turn': 1, 'log': ["战斗开始！"]})
        st.rerun()
else:
    st.subheader(f"第 {st.session_state.turn} 回合 | {st.session_state.p} vs {st.session_state.o}")
    col1, col2 = st.columns(2)
    col1.metric("你的 HP", st.session_state.p_hp)
    col2.metric("对手 HP", st.session_state.o_hp)
    st.progress(st.session_state.sp/100, text=f"当前 SP: {st.session_state.sp}")

    action = st.radio("选择指令:", ["普通攻击 (5SP)", f"技能: {chars[st.session_state.p]['skill']} (25SP)", f"强化: {chars[st.session_state.p]['buff']} (67SP)", f"大招: {chars[st.session_state.p]['ult']} (78SP)"])
    
    if st.button("执行回合"):
        costs = {"普通": 5, "技能": 25, "强化": 67, "大招": 78}
        cost = next(v for k, v in costs.items() if k in action)
        
        if st.session_state.sp < cost:
            st.error("SP 不足！")
        else:
            # 玩家攻击
            dmg = chars[st.session_state.p]['atk'] + (20 if "强化" in action else (60 if "大招" in action else 0))
            st.session_state.o_hp -= dmg
            st.session_state.sp = min(100, st.session_state.sp - cost + 10) 
            st.session_state.log.append(f"第{st.session_state.turn}回合: 你使用 {action}，造成 {dmg} 点伤害。")
            
            # 对手反击逻辑：随机选择招式
            o_char = chars[st.session_state.o]
            o_moves = [("普通攻击", o_char['atk']), (o_char['skill'], o_char['atk']+10), (o_char['ult'], o_char['atk']+40)]
            m_name, m_dmg = random.choice(o_moves)
            st.session_state.p_hp -= m_dmg
            st.session_state.log.append(f"对手 {st.session_state.o} 反击：使出「{m_name}」，造成 {m_dmg} 点伤害。")
            
            st.session_state.turn += 1
            st.rerun()

    st.write("### 战斗日志")
    for l in reversed(st.session_state.log[-5:]): st.write(l)
    
    if st.session_state.p_hp <= 0 or st.session_state.o_hp <= 0:
        st.success("战斗结束！")
        if st.button("再来一局"): st.session_state.started = False; st.rerun()
