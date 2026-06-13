import streamlit as st
import random

# 角色数据
chars = {
    "Shaw Zer": {"hp": 150, "atk": 15, "skill": "撒娇求带", "ult": "极限嘴硬"},
    "Zhi Wei": {"hp": 130, "atk": 25, "skill": "雷达扫描", "ult": "学弟捕捉"},
    "Qi Yu": {"hp": 200, "atk": 12, "skill": "Teh O Ais补给", "ult": "虚无入定"},
    "Jun Zi": {"hp": 110, "atk": 35, "skill": "哈士奇撕咬", "ult": "狂暴觉醒"},
    "Keith Goh": {"hp": 170, "atk": 20, "skill": "动漫吐槽", "ult": "二次元审判"}
}

st.title("⚔️ 隆中华：嘴硬争霸赛")

# 初始化状态
if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    p = st.selectbox("选择角色:", list(chars.keys()))
    if st.button("开始挑战"):
        o = random.choice([c for c in chars if c != p])
        st.session_state.update({
            'started': True, 'p': p, 'o': o, 'p_hp': chars[p]['hp'], 
            'o_hp': chars[o]['hp'], 'sp': 40, 'turn': 1, 'log': ["战斗开始！"]
        })
        st.rerun()
else:
    # 稳定读取状态
    st.subheader(f"第 {st.session_state.turn} 回合 | {st.session_state.p} vs {st.session_state.o}")
    
    col1, col2 = st.columns(2)
    col1.metric("HP", st.session_state.p_hp)
    col2.metric("对手 HP", st.session_state.o_hp)
    st.progress(st.session_state.sp/100, text=f"SP: {st.session_state.sp}/100")

    action = st.radio("战术:", ["普通攻击 (5SP)", f"{chars[st.session_state.p]['skill']} (25SP)", f"大招: {chars[st.session_state.p]['ult']} (78SP)"])
    
    if st.button("确认出招"):
        cost = 5 if "普通" in action else (25 if "技能" in action else 78)
        if st.session_state.sp < cost:
            st.error("SP不足！")
        else:
            st.session_state.sp = min(100, st.session_state.sp - cost + 10)
            dmg = chars[st.session_state.p]['atk'] + (25 if "大招" in action else 0)
            st.session_state.o_hp -= dmg
            st.session_state.p_hp -= chars[st.session_state.o]['atk']
            st.session_state.turn += 1
            st.rerun()

    if st.session_state.p_hp <= 0 or st.session_state.o_hp <= 0:
        st.success("比赛结束！" if st.session_state.o_hp <= 0 else "你输了！")
        if st.button("重来"):
            st.session_state.started = False
            st.rerun()
