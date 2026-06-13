import streamlit as st
import random

# 角色定义：加入特殊技能
characters = {
    "Shaw Zer": {"hp": 150, "atk": 15, "skill": "【撒娇求带】：回复20点HP"},
    "Zhi Wei": {"hp": 130, "atk": 25, "skill": "【学弟雷达】：无视防御直接扣20点"},
    "Qi Yu": {"hp": 200, "atk": 10, "skill": "【Teh O Ais 补给】：回复50点HP"},
    "Jun Zi": {"hp": 120, "atk": 30, "skill": "【哈士奇狂暴】：伤害翻倍"},
    "Keith Goh": {"hp": 180, "atk": 20, "skill": "【中二审判】：对敌方造成30点伤害"}
}

st.title("🔥 隆中华：巅峰大乱斗 v2.0")

if 'game' not in st.session_state:
    st.session_state.game = {'started': False, 'turn': 0}

if not st.session_state.game['started']:
    player = st.selectbox("选出你的大将:", list(characters.keys()))
    if st.button("进入战斗"):
        st.session_state.game = {
            'started': True, 'p': player, 'o': random.choice([c for c in characters if c != player]),
            'p_hp': characters[player]['hp'], 'o_hp': characters[st.session_state.game.get('o', 'Qi Yu')]['hp'],
            'log': ["战斗开始！"]
        }
        st.rerun()
else:
    # 战斗逻辑
    st.write(f"### 正在对战: {st.session_state.game['p']} vs {st.session_state.game['o']}")
    col1, col2 = st.columns(2)
    col1.metric("你的 HP", st.session_state.game['p_hp'])
    col2.metric("对手 HP", st.session_state.game['o_hp'])

    # 动作选择
    action = st.radio("选择你的回合操作:", ["普通嘴硬攻击", "使用必杀技", "去 Mamak 档加冰"])
    
    if st.button("确认出招"):
        log = st.session_state.game['log']
        if action == "普通嘴硬攻击":
            dmg = characters[st.session_state.game['p']]['atk'] + random.randint(0, 10)
            st.session_state.game['o_hp'] -= dmg
            log.append(f"你造成了 {dmg} 点嘴硬伤害！")
        elif action == "使用必杀技":
            if "补给" in characters[st.session_state.game['p']]['skill']:
                st.session_state.game['p_hp'] += 50
                log.append("你喝了 Teh O Ais，HP 回复 50！")
            else:
                st.session_state.game['o_hp'] -= 30
                log.append("必杀技命中！对手扣 30 HP！")
        else:
            st.session_state.game['p_hp'] += 10
            log.append("你喝了杯冰水，稍微冷静了一下，回复 10 HP。")

        # 对手反击
        if st.session_state.game['o_hp'] > 0:
            o_dmg = characters[st.session_state.game['o']]['atk'] + random.randint(0, 5)
            st.session_state.game['p_hp'] -= o_dmg
            log.append(f"对手反击了，对你造成了 {o_dmg} 点伤害！")

        # 胜负判定
        if st.session_state.game['p_hp'] <= 0:
            st.error("你被对面搞破防了！")
            st.session_state.game['started'] = False
        elif st.session_state.game['o_hp'] <= 0:
            st.success("你赢得了这场嘴硬巅峰之战！")
            st.session_state.game['started'] = False
        st.rerun()

    st.write("---")
    st.write("### 战斗日志:")
    for entry in reversed(st.session_state.game['log'][-5:]):
        st.write(f"- {entry}")
