import streamlit as st
import random

# 角色定义
characters = {
    "Shaw Zer": {"hp": 100, "atk": 15, "desc": "🐰 掉星嘴硬男娘"},
    "Zhi Wei": {"hp": 100, "atk": 20, "desc": "👁️ 抓学弟雷达官"},
    "Qi Yu": {"hp": 100, "atk": 10, "desc": "🍹 虚无 Teh O Ais 仙人"},
    "Jun Zi": {"hp": 100, "atk": 18, "desc": "🐶 智商1% 快乐哈士奇"},
    "Keith Goh": {"hp": 100, "atk": 25, "desc": "👴 50岁暴走老御宅"}
}

st.title("🔥 隆中华嘴硬大赛 (Trash Talk Arena)")

if 'game_started' not in st.session_state:
    st.session_state.game_started = False

if not st.session_state.game_started:
    player = st.selectbox("选择你的角色:", list(characters.keys()))
    if st.button("开始比赛"):
        st.session_state.player = player
        st.session_state.opponent = random.choice([c for c in characters if c != player])
        st.session_state.p_hp = characters[player]["hp"]
        st.session_state.o_hp = characters[st.session_state.opponent]["hp"]
        st.session_state.game_started = True
        st.rerun()
else:
    st.write(f"### {st.session_state.player} vs {st.session_state.opponent}")
    col1, col2 = st.columns(2)
    col1.metric("你的 HP", st.session_state.p_hp)
    col2.metric(f"{st.session_state.opponent} HP", st.session_state.o_hp)
    
    move = st.text_input("输入你的嘴硬攻击语录:")
    if st.button("发送攻击"):
        # 简单的伤害逻辑
        dmg = len(move) % 20 + characters[st.session_state.player]["atk"]
        st.session_state.o_hp -= dmg
        st.write(f"你使用了嘴硬攻击：'{move}'，造成了 {dmg} 点伤害！")
        
        if st.session_state.o_hp <= 0:
            st.success(f"{st.session_state.opponent} 破防了！你赢了！")
            st.session_state.game_started = False
        else:
            # 对手反击
            o_dmg = characters[st.session_state.opponent]["atk"] + random.randint(0, 10)
            st.session_state.p_hp -= o_dmg
            st.write(f"{st.session_state.opponent} 反击了！对你造成了 {o_dmg} 点伤害！")
            if st.session_state.p_hp <= 0:
                st.error("你破防了... 游戏结束！")
                st.session_state.game_started = False
