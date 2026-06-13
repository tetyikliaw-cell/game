import streamlit as st
import random

# 角色数据：包含普通技能(25SP) 和 强化技能(67SP)
chars = {
    "Shaw Zer": {"hp": 150, "atk": 15, "skill": "撒娇求带", "buff": "极限嘴硬"},
    "Zhi Wei": {"hp": 130, "atk": 25, "skill": "雷达扫描", "buff": "学弟捕捉"},
    "Qi Yu": {"hp": 200, "atk": 12, "skill": "Teh O Ais补给", "buff": "虚无入定"},
    "Jun Zi": {"hp": 110, "atk": 35, "skill": "哈士奇撕咬", "buff": "狂暴觉醒"},
    "Keith Goh": {"hp": 170, "atk": 20, "skill": "动漫吐槽", "buff": "二次元审判"}
}

st.title("⚔️ 隆中华：嘴硬争霸赛 v3.0")

# 初始化状态
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

    action = st.radio("选择指令:", ["普通攻击 (5SP)", f"技能: {chars[st.session_state.p]['skill']} (25SP)", f"强化: {chars[st.session_state.p]['buff']} (67SP)"])
    
    if st.button("执行回合"):
        cost = 5 if "普通" in action else (25 if "技能" in action else 67)
        if st.session_state.sp < cost:
            st.error("SP 不足！")
        else:
            # 结算逻辑
            dmg = chars[st.session_state.p]['atk'] + (20 if "强化" in action else 0)
            st.session_state.o_hp -= dmg
            st.session_state.sp = min(100, st.session_state.sp - cost + 10) # 回合结束回10
            st.session_state.log.append(f"第{st.session_state.turn}回合: 你使用了 {action}，造成 {dmg} 点伤害。")
            
            # 对手反击
            o_dmg = chars[st.session_state.o]['atk']
            st.session_state.p_hp -= o_dmg
            st.session_state.log.append(f"对手 {st.session_state.o} 反击，你损失 {o_dmg} HP。")
            
            st.session_state.turn += 1
            st.rerun()

    st.write("### 战斗日志")
    for l in reversed(st.session_state.log[-5:]): st.write(l)
    
    if st.session_state.p_hp <= 0 or st.session_state.o_hp <= 0:
        st.success("战斗结束！")
        if st.button("再来一局"): st.session_state.started = False; st.rerun()
