import streamlit as st
import random

# 定义角色和他们的 3 张技能牌
cards = {
    "德育月": {"hp": 250, "deck": {"嘲讽重击": 50, "降智打击": 40, "终极处刑": 91}},
    "Shaw Zer": {"hp": 150, "deck": {"撒娇": 20, "极限嘴硬": 35, "掉星暴走": 60}},
    "Jun Zi": {"hp": 110, "deck": {"哈士奇撕咬": 45, "狂暴觉醒": 30, "哈士奇陨石": 70}},
    "Zhi Wei": {"hp": 130, "deck": {"雷达扫描": 25, "学弟捕捉": 35, "雷达过载": 65}},
    "Qi Yu": {"hp": 200, "deck": {"Teh O Ais": 15, "虚无入定": 30, "冰封宇宙": 55}},
    "Keith Goh": {"hp": 170, "deck": {"动漫吐槽": 20, "二次元结界": 40, "老宅男审判": 60}}
}

st.title("🃏 隆中华：智障卡牌对决")

if 'game' not in st.session_state:
    st.session_state.game = {'started': False, 'log': []}

if not st.session_state.game['started']:
    if st.button("开始决斗"):
        p, o = random.sample(list(cards.keys()), 2)
        st.session_state.game.update({
            'started': True, 'p': p, 'o': o, 
            'p_hp': cards[p]['hp'], 'o_hp': cards[o]['hp'],
            'turn': 1, 'log': ["决斗开始！请出牌！"]
        })
        st.rerun()
else:
    col1, col2 = st.columns(2)
    col1.metric(f"你 ({st.session_state.game['p']})", st.session_state.game['p_hp'])
    col2.metric(f"对手 ({st.session_state.game['o']})", st.session_state.game['o_hp'])
    
    # 玩家操作区
    p_deck = cards[st.session_state.game['p']]['deck']
    choice = st.radio("选择你的回合卡牌:", list(p_deck.keys()))
    
    if st.button("确认出牌"):
        # 你的伤害
        dmg_p = p_deck[choice]
        # 对手随机出牌
        o_choice = random.choice(list(cards[st.session_state.game['o']]['deck'].keys()))
        dmg_o = cards[st.session_state.game['o']]['deck'][o_choice]
        
        st.session_state.game['o_hp'] -= dmg_p
        st.session_state.game['p_hp'] -= dmg_o
        st.session_state.game['log'].append(f"你用了{choice}造成{dmg_p}伤，对手用了{o_choice}造成{dmg_o}伤")
        
        if st.session_state.game['o_hp'] <= 0 or st.session_state.game['p_hp'] <= 0:
            st.balloons()
            st.session_state.game['started'] = False
        st.rerun()

    st.write("### 战斗记录")
    for l in reversed(st.session_state.game['log'][-5:]): st.write(l)
