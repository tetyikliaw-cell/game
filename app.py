import streamlit as st
import random

# --- 之前的所有特点完整保留 ---
skills_data = {
    "普通攻击": {"cost": 5, "dmg": 15},
    "技能打击": {"cost": 25, "dmg": 35},
    "极限嘲讽": {"cost": 67, "dmg": 45},
    "大招终结": {"cost": 78, "dmg": 91}
}

taunts = ["笑死，你会玩吗？", "隆中华没人了吗？", "太弱了，换个姿势再来！", "这是你最强的招？"]

# --- 初始化 (保留之前的 Session State) ---
if 'sp' not in st.session_state:
    st.session_state.update({
        'sp': 150, 'hp': 250, 'log': ["欢迎来到隆中华大乱斗，开始你的回合！"], 
        'crit_chance': 0.2
    })

st.title("🃏 隆中华：大乱斗终极版")

# --- 战斗操作 ---
choice = st.radio("选择你的攻击:", list(skills_data.keys()))

if st.button("执行行动"):
    skill = skills_data[choice]
    
    # 【特点 1】严苛的 SP 限制：不够就不让执行
    if st.session_state.sp < skill["cost"]:
        st.error(f"⚠️ SP不足！需要 {skill['cost']}，你当前只有 {st.session_state.sp}。")
    else:
        # 【特点 2】暴击机制 (20% 概率伤害翻倍)
        is_crit = random.random() < st.session_state.crit_chance
        final_dmg = skill["dmg"] * 2 if is_crit else skill["dmg"]
        
        # 【特点 3】战斗日志更新
        crit_msg = "！暴击！" if is_crit else ""
        st.session_state.sp -= skill["cost"]
        st.session_state.hp -= final_dmg
        
        # 【特点 4】随机嘲讽系统
        taunt = random.choice(taunts)
        st.session_state.log.append(f"使用了 {choice}{crit_msg}，造成 {final_dmg} 伤害。对手嘲讽：{taunt}")
        
        # 【特点 5】SP 自动回复 (限制上限)
        st.session_state.sp = min(150, st.session_state.sp + 10)
        st.rerun()

# --- 状态显示 ---
st.write(f"### HP: {st.session_state.hp} | SP: {st.session_state.sp}")
st.progress(st.session_state.sp / 150)

st.write("### 战斗记录")
for msg in reversed(st.session_state.log[-5:]):
    st.write(msg)
