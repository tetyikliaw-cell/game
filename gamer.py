import streamlit as st

# 直接嵌入你的游戏HTML文件
# 记得把 'game.html' 换成你游戏文件的实际名字
with open("game.html", "r", encoding="utf-8") as f:
    html_code = f.read()

# 使用 st.html 直接渲染你的游戏
st.html(html_code)
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>魂斗罗 · 手机版 · 救男娘</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            touch-action: none;
        }
        body {
            background: #0a0a1a;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            font-family: 'Courier New', monospace;
            user-select: none;
            -webkit-user-select: none;
            touch-action: none;
        }
        #gameWrap {
            background: #14142a;
            padding: 8px;
            border-radius: 16px;
            box-shadow: 0 0 60px rgba(0, 200, 255, 0.3);
            border: 2px solid #0cf;
            width: 100%;
            max-width: 600px;
            aspect-ratio: 16/9;
            position: relative;
        }
        canvas {
            display: block;
            margin: 0 auto;
            background: #1a2a3a;
            border-radius: 10px;
            image-rendering: pixelated;
            width: 100%;
            height: 100%;
            touch-action: none;
            cursor: none;
        }
        #controls {
            position: absolute;
            bottom: 10px;
            left: 0;
            right: 0;
            display: flex;
            justify-content: space-between;
            padding: 0 12px;
            pointer-events: none;
            z-index: 10;
        }
        #controls button {
            pointer-events: auto;
            background: rgba(255, 255, 255, 0.15);
            border: 2px solid rgba(255, 255, 255, 0.3);
            color: #fff;
            font-size: 12px;
            font-weight: bold;
            padding: 8px 14px;
            border-radius: 30px;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            text-shadow: 0 0 8px rgba(0,0,0,0.8);
            touch-action: manipulation;
            min-width: 50px;
            text-align: center;
        }
        #controls button:active {
            background: rgba(255, 255, 255, 0.35);
            transform: scale(0.92);
        }
        #controls .left-btns {
            display: flex;
            gap: 8px;
        }
        #controls .right-btns {
            display: flex;
            gap: 8px;
        }
        #controls .btn-jump {
            background: rgba(0, 200, 255, 0.25);
            border-color: rgba(0, 200, 255, 0.5);
        }
        #controls .btn-shoot {
            background: rgba(255, 50, 50, 0.25);
            border-color: rgba(255, 50, 50, 0.5);
            font-size: 16px;
            padding: 8px 20px;
        }
        #controls .btn-dash {
            background: rgba(255, 200, 0, 0.2);
            border-color: rgba(255, 200, 0, 0.4);
        }
        #controls .btn-shield {
            background: rgba(0, 255, 200, 0.2);
            border-color: rgba(0, 255, 200, 0.4);
        }
        #info {
            display: none;
        }
        /* 触摸提示 */
        #touchHint {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: rgba(255,255,255,0.3);
            font-size: 14px;
            text-align: center;
            pointer-events: none;
            z-index: 5;
            background: rgba(0,0,0,0.5);
            padding: 16px 24px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        @media (max-width: 500px) {
            #controls button {
                font-size: 10px;
                padding: 5px 10px;
                min-width: 40px;
            }
            #controls .btn-shoot {
                font-size: 14px;
                padding: 5px 16px;
            }
        }
    </style>
</head>
<body>
    <div id="gameWrap">
        <canvas id="gameCanvas" width="1200" height="640"></canvas>
        <div id="touchHint">← 左滑移动 · 右滑瞄准 · 按钮射击 →</div>
        <div id="controls">
            <div class="left-btns">
                <button class="btn-jump" id="btnJump">⬆跳</button>
                <button class="btn-dash" id="btnDash">💨冲刺</button>
            </div>
            <div class="right-btns">
                <button class="btn-shield" id="btnShield">🛡️护盾</button>
                <button class="btn-shoot" id="btnShoot">🔫射击</button>
            </div>
        </div>
    </div>
    <script>
        // ================================================================
        //  魂斗罗 · 手机触摸版 · 完整游戏
        // ================================================================

        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const W = 1200,
            H = 640,
            GROUND_Y = 550,
            GRAVITY = 0.65,
            PLAYER_SPEED = 4.5,
            JUMP_FORCE = -11.5;
        const LEVEL_WIDTH = 5000,
            MAX_LEVEL = 5,
            MAX_HP = 100;

        // ----- 触摸输入 -----
        const touch = {
            leftActive: false,
            leftX: 0,
            leftY: 0,
            rightActive: false,
            rightX: 0,
            rightY: 0,
            shootPressed: false,
            jumpPressed: false,
            dashPressed: false,
            shieldPressed: false
        };

        // 键盘保留（用于调试）
        const keys = { a: false, d: false, w: false, space: false, shift: false, e: false };

        // ----- 鼠标/触摸 事件 -----
        function getTouchPos(e) {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const touch = e.touches[0];
            return {
                x: (touch.clientX - rect.left) * scaleX,
                y: (touch.clientY - rect.top) * scaleY
            };
        }

        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;

            for (let t of e.touches) {
                const tx = (t.clientX - rect.left) * scaleX;
                const ty = (t.clientY - rect.top) * scaleY;

                // 左半屏 = 移动控制
                if (tx < canvas.width * 0.45) {
                    touch.leftActive = true;
                    touch.leftX = tx;
                    touch.leftY = ty;
                }
                // 右半屏 = 瞄准控制
                else {
                    touch.rightActive = true;
                    touch.rightX = tx;
                    touch.rightY = ty;
                    // 同时触发射击（自动开火模式，但用按钮更精准）
                }
            }

            // 如果只有单指，且点击的是右侧，视为瞄准+射击
            if (e.touches.length === 1) {
                const t = e.touches[0];
                const tx = (t.clientX - rect.left) * scaleX;
                const ty = (t.clientY - rect.top) * scaleY;
                if (tx >= canvas.width * 0.45) {
                    touch.rightActive = true;
                    touch.rightX = tx;
                    touch.rightY = ty;
                }
            }
        }, { passive: false });

        canvas.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;

            // 重置触摸状态
            touch.leftActive = false;
            touch.rightActive = false;

            for (let t of e.touches) {
                const tx = (t.clientX - rect.left) * scaleX;
                const ty = (t.clientY - rect.top) * scaleY;

                if (tx < canvas.width * 0.45) {
                    touch.leftActive = true;
                    touch.leftX = tx;
                    touch.leftY = ty;
                } else {
                    touch.rightActive = true;
                    touch.rightX = tx;
                    touch.rightY = ty;
                }
            }
        }, { passive: false });

        canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            touch.leftActive = false;
            touch.rightActive = false;
            // 保留按钮状态
        }, { passive: false });

        // ----- 按钮事件 -----
        document.getElementById('btnJump').addEventListener('touchstart', (e) => { e.preventDefault();
            touch.jumpPressed = true; });
        document.getElementById('btnJump').addEventListener('touchend', (e) => { e.preventDefault();
            touch.jumpPressed = false; });
        document.getElementById('btnJump').addEventListener('mousedown', () => { touch.jumpPressed = true; });
        document.getElementById('btnJump').addEventListener('mouseup', () => { touch.jumpPressed = false; });

        document.getElementById('btnDash').addEventListener('touchstart', (e) => { e.preventDefault();
            touch.dashPressed = true; });
        document.getElementById('btnDash').addEventListener('touchend', (e) => { e.preventDefault();
            touch.dashPressed = false; });
        document.getElementById('btnDash').addEventListener('mousedown', () => { touch.dashPressed = true; });
        document.getElementById('btnDash').addEventListener('mouseup', () => { touch.dashPressed = false; });

        document.getElementById('btnShield').addEventListener('touchstart', (e) => { e.preventDefault();
            touch.shieldPressed = true; });
        document.getElementById('btnShield').addEventListener('touchend', (e) => { e.preventDefault();
            touch.shieldPressed = false; });
        document.getElementById('btnShield').addEventListener('mousedown', () => { touch.shieldPressed = true; });
        document.getElementById('btnShield').addEventListener('mouseup', () => { touch.shieldPressed = false; });

        document.getElementById('btnShoot').addEventListener('touchstart', (e) => { e.preventDefault();
            touch.shootPressed = true; });
        document.getElementById('btnShoot').addEventListener('touchend', (e) => { e.preventDefault();
            touch.shootPressed = false; });
        document.getElementById('btnShoot').addEventListener('mousedown', () => { touch.shootPressed = true; });
        document.getElementById('btnShoot').addEventListener('mouseup', () => { touch.shootPressed = false; });

        // ----- 键盘兼容（桌面调试）-----
        document.addEventListener('keydown', (e) => {
            const k = e.key.toLowerCase();
            if (k === 'a') keys.a = true;
            if (k === 'd') keys.d = true;
            if (k === 'w') keys.w = true;
            if (k === ' ') { keys.space = true;
                e.preventDefault(); }
            if (k === 'shift') { keys.shift = true;
                e.preventDefault(); }
            if (k === 'e') keys.e = true;
            if (gameState === 'MENU') {
                if (k === '1') { selectedHero = 0;
                    startGame(); }
                if (k === '2') { selectedHero = 1;
                    startGame(); }
                if (k === '3') { selectedHero = 2;
                    startGame(); }
            }
            if ((gameState === 'GAMEOVER' || gameState === 'WIN') && k === 'r') resetGame();
        });
        document.addEventListener('keyup', (e) => {
            const k = e.key.toLowerCase();
            if (k === 'a') keys.a = false;
            if (k === 'd') keys.d = false;
            if (k === 'w') keys.w = false;
            if (k === ' ') { keys.space = false;
                e.preventDefault(); }
            if (k === 'shift') { keys.shift = false;
                e.preventDefault(); }
            if (k === 'e') keys.e = false;
        });

        // ----- 游戏状态 -----
        let gameState = 'MENU',
            selectedHero = 0,
            currentLevel = 1,
            score = 0,
            frameCount = 0,
            camera = { x: 0 };
        let loadingProgress = 0,
            transitionTimer = 0,
            transitionMessage = '',
            showSkillUnlock = false,
            skillUnlockText = '',
            skillUnlockTimer = 0;
        let skills = { doubleJump: false, dash: false, shield: false, attackUp: false, rapidFire: false,
            bulletPenetrate: false, bulletSplit: false };
        let shieldTimer = 0;

        let player = {
            x: 120,
            y: GROUND_Y - 56,
            w: 38,
            h: 56,
            vx: 0,
            vy: 0,
            onGround: false,
            facing: 1,
            hp: MAX_HP,
            maxHp: MAX_HP,
            shootCooldown: 0,
            baseShootCooldown: 8,
            canDoubleJump: false,
            hasDoubleJumped: false,
            dashCooldown: 0,
            isDashing: false,
            dashTimer: 0,
            invincible: 0,
            dead: false,
            attackPower: 2,
            walkCycle: 0
        };
        let playerBullets = [],
            enemyBullets = [],
            enemies = [],
            obstacles = [],
            medicalItems = [],
            particles = [],
            slashEffects = [];
        let flag = null,
            boss = null,
            bossActive = false;
        const taunts = ['你是个小男娘 😏', '就这？回去当gay吧 🏳️‍🌈', '连男娘都救不了，弱爆了 💩', 'Boss都笑了 🤣', '建议你换个游戏 🎮'];

        function rectCollide(a, b) { return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y; }

        function spawnParticles(x, y, color, count = 30, speed = 7, sizeVar = 5) {
            for (let i = 0; i < count; i++) {
                const ang = Math.random() * Math.PI * 2,
                    sp = 1 + Math.random() * speed;
                particles.push({ x, y, vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp - 1, life: 20 + Math.random() * 35,
                    maxLife: 55, size: 2 + Math.random() * sizeVar, color: color || `hsl(${Math.random()*60+20},80%,60%)` });
            }
        }

        // ================================================================
        //  绘制玩家（精致手绘）
        // ================================================================
        function drawPlayer(ctx, x, y, type, facing, invincible, shieldActive) {
            if (invincible && Math.floor(Date.now() / 100) % 2 === 0) { ctx.globalAlpha = 0.4; }
            if (shieldActive) {
                ctx.shadowColor = '#00FFFF';
                ctx.shadowBlur = 60;
                ctx.strokeStyle = 'rgba(0,255,255,0.7)';
                ctx.lineWidth = 5;
                ctx.beginPath();
                ctx.arc(x + 19, y + 28, 44, 0, Math.PI * 2);
                ctx.stroke();
                for (let i = 0; i < 12; i++) {
                    const a = i / 12 * Math.PI * 2;
                    ctx.strokeStyle = 'rgba(0,255,255,0.2)';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(x + 19 + Math.cos(a) * 38, y + 28 + Math.sin(a) * 38);
                    ctx.lineTo(x + 19 + Math.cos(a + 0.3) * 44, y + 28 + Math.sin(a + 0.3) * 44);
                    ctx.stroke();
                }
                ctx.shadowBlur = 0;
            }
            ctx.save();
            ctx.translate(x, y);
            const f = facing;
            const legSwing = Math.sin(player.walkCycle) * 5;

            // 头部
            const headGrad = ctx.createRadialGradient(13, 8, 4, 19, 12, 16);
            headGrad.addColorStop(0, '#FFE8D0');
            headGrad.addColorStop(1, '#D2A080');
            ctx.fillStyle = headGrad;
            ctx.beginPath();
            ctx.ellipse(19, 12, 16, 18, 0, 0, Math.PI * 2);
            ctx.fill();
            // 头发
            if (type === 0) {
                ctx.fillStyle = '#D4A017';
                ctx.beginPath();
                ctx.ellipse(19, 4, 18, 12, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#C89010';
                ctx.beginPath();
                ctx.ellipse(10, 2, 6, 8, 0.3, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(28, 2, 6, 8, -0.3, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#6B3A1A';
                ctx.fillRect(0, -4, 38, 8);
                ctx.fillRect(6, -18, 26, 16);
                ctx.fillStyle = '#8B5A2B';
                ctx.fillRect(-2, -6, 42, 4);
                ctx.fillStyle = '#B8860B';
                ctx.fillRect(14, -12, 10, 6);
            } else if (type === 1) {
                ctx.fillStyle = '#3A2A1A';
                ctx.beginPath();
                ctx.ellipse(19, 4, 18, 10, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#2A1A0A';
                ctx.beginPath();
                ctx.ellipse(10, 2, 5, 6, 0.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(28, 2, 5, 6, -0.2, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#2E4A2E';
                ctx.beginPath();
                ctx.ellipse(19, -2, 20, 8, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#1B3B1B';
                ctx.fillRect(0, -6, 38, 6);
                ctx.fillStyle = '#4A6B4A';
                ctx.fillRect(14, -4, 10, 2);
            } else {
                ctx.fillStyle = '#FF00FF';
                ctx.fillRect(8, -4, 22, 10);
                ctx.fillStyle = '#00FFFF';
                ctx.fillRect(12, -6, 16, 4);
                ctx.fillStyle = '#FF00FF';
                ctx.fillRect(4, 0, 32, 4);
                ctx.shadowColor = '#00FFFF';
                ctx.shadowBlur = 20;
                ctx.fillStyle = 'rgba(0,255,255,0.5)';
                ctx.fillRect(2, 4, 16, 10);
                ctx.fillRect(20, 4, 16, 10);
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#00FFFF';
                ctx.fillRect(4, 6, 12, 6);
                ctx.fillRect(22, 6, 12, 6);
                ctx.shadowColor = '#FF00FF';
                ctx.shadowBlur = 15;
                ctx.fillStyle = '#FF00FF';
                ctx.beginPath();
                ctx.arc(10, 9, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#FFF';
                ctx.beginPath();
                ctx.arc(8, 7, 2, 0, Math.PI * 2);
                ctx.fill();
            }
            // 眼睛
            ctx.fillStyle = '#FFF';
            ctx.beginPath();
            ctx.ellipse(14, 12, 5, 6, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(24, 12, 5, 6, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#2C2C2C';
            ctx.beginPath();
            ctx.ellipse(14, 12, 3, 5, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(24, 12, 3, 5, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#FFF';
            ctx.beginPath();
            ctx.arc(15, 10, 1.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.arc(25, 10, 1.5, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#2C2C2C';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(10, 8);
            ctx.lineTo(17, 7);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(21, 7);
            ctx.lineTo(28, 8);
            ctx.stroke();
            ctx.strokeStyle = '#8B4A4A';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(19, 18, 4, 0.1, Math.PI - 0.1);
            ctx.stroke();

            // 颈部
            ctx.fillStyle = '#D2A080';
            ctx.fillRect(15, 26, 8, 6);

            // 躯干
            let gradBody;
            if (type === 0) { gradBody = ctx.createLinearGradient(4, 30, 34, 56);
                gradBody.addColorStop(0, '#E8C9A0');
                gradBody.addColorStop(1, '#B89070'); } else if (type === 1) { gradBody = ctx.createLinearGradient(4, 30,
                    34, 56);
                gradBody.addColorStop(0, '#5A7A5A');
                gradBody.addColorStop(1, '#3A5A3A'); } else { gradBody = ctx.createLinearGradient(4, 30, 34, 56);
                gradBody.addColorStop(0, '#3A2A6A');
                gradBody.addColorStop(1, '#1A0A3A'); }
            ctx.fillStyle = gradBody;
            ctx.beginPath();
            ctx.roundRect(4, 30, 30, 28, 4);
            ctx.fill();
            ctx.fillStyle = 'rgba(255,255,255,0.15)';
            for (let i = 0; i < 3; i++) { ctx.fillRect(10, 34 + i * 8, 18, 2); }
            if (type === 1) { ctx.fillStyle = '#FFD700';
                ctx.fillRect(22, 32, 6, 6);
                ctx.fillStyle = '#FFF';
                ctx.font = '6px sans-serif';
                ctx.fillText('★', 23, 38); }
            if (type === 2) { ctx.shadowColor = '#FF00FF';
                ctx.shadowBlur = 10;
                ctx.fillStyle = '#FF00FF';
                ctx.fillRect(2, 34, 4, 20);
                ctx.fillStyle = '#00FFFF';
                ctx.fillRect(32, 34, 4, 20);
                ctx.shadowBlur = 0; }

            // 手臂+武器
            ctx.fillStyle = (type === 0) ? '#D2A080' : (type === 1) ? '#4A6B4A' : '#8899AA';
            if (f === 1) {
                ctx.fillRect(32, 32, 10, 8);
                ctx.fillRect(36, 38, 6, 12);
                ctx.fillRect(38, 48, 8, 6);
                ctx.fillRect(38, 52, 4, 4);
                ctx.fillRect(42, 52, 4, 4);
                const weapGrad = ctx.createLinearGradient(40, 34, 56, 34);
                weapGrad.addColorStop(0, '#C0C0C0');
                weapGrad.addColorStop(0.5, '#FFF');
                weapGrad.addColorStop(1, '#888');
                ctx.fillStyle = weapGrad;
                ctx.fillRect(40, 32, 20, 6);
                if (type === 0) { ctx.fillStyle = '#8B4513';
                    ctx.fillRect(44, 30, 4, 10);
                    ctx.fillStyle = '#B8860B';
                    ctx.fillRect(48, 33, 2, 4); } else if (type === 1) { ctx.fillStyle = '#222';
                    ctx.fillRect(52, 28, 8, 12);
                    ctx.fillStyle = '#444';
                    ctx.fillRect(48, 30, 4, 8); } else { ctx.shadowColor = '#00FFFF';
                    ctx.shadowBlur = 25;
                    ctx.fillStyle = '#00BFFF';
                    ctx.fillRect(44, 30, 16, 8);
                    ctx.shadowBlur = 0; }
                ctx.fillRect(0, 34, 10, 8);
                ctx.fillRect(2, 40, 6, 14);
                ctx.fillRect(0, 52, 6, 6);
                ctx.fillRect(4, 52, 6, 6);
            } else {
                ctx.fillRect(-2, 32, 10, 8);
                ctx.fillRect(-4, 38, 6, 12);
                ctx.fillRect(-4, 48, 8, 6);
                ctx.fillRect(-4, 52, 4, 4);
                ctx.fillRect(0, 52, 4, 4);
                const weapGrad = ctx.createLinearGradient(-12, 34, -28, 34);
                weapGrad.addColorStop(0, '#C0C0C0');
                weapGrad.addColorStop(0.5, '#FFF');
                weapGrad.addColorStop(1, '#888');
                ctx.fillStyle = weapGrad;
                ctx.fillRect(-28, 32, 20, 6);
                if (type === 0) { ctx.fillStyle = '#8B4513';
                    ctx.fillRect(-20, 30, 4, 10);
                    ctx.fillStyle = '#B8860B';
                    ctx.fillRect(-16, 33, 2, 4); } else if (type === 1) { ctx.fillStyle = '#222';
                    ctx.fillRect(-24, 28, 8, 12);
                    ctx.fillStyle = '#444';
                    ctx.fillRect(-20, 30, 4, 8); } else { ctx.shadowColor = '#00FFFF';
                    ctx.shadowBlur = 25;
                    ctx.fillStyle = '#00BFFF';
                    ctx.fillRect(-28, 30, 16, 8);
                    ctx.shadowBlur = 0; }
                ctx.fillRect(28, 34, 10, 8);
                ctx.fillRect(30, 40, 6, 14);
                ctx.fillRect(28, 52, 6, 6);
                ctx.fillRect(34, 52, 6, 6);
            }

            // 腿
            ctx.fillStyle = (type === 0) ? '#5C3A1A' : (type === 1) ? '#2E4A2E' : '#8800AA';
            ctx.fillRect(6, 54 + legSwing, 10, 14);
            ctx.fillRect(4, 66 + legSwing, 14, 8);
            ctx.fillStyle = '#333';
            ctx.fillRect(4, 72 + legSwing, 14, 8);
            ctx.fillStyle = '#555';
            ctx.fillRect(2, 76 + legSwing, 18, 4);
            ctx.fillStyle = (type === 0) ? '#5C3A1A' : (type === 1) ? '#2E4A2E' : '#8800AA';
            ctx.fillRect(22, 54 - legSwing, 10, 14);
            ctx.fillRect(20, 66 - legSwing, 14, 8);
            ctx.fillStyle = '#333';
            ctx.fillRect(20, 72 - legSwing, 14, 8);
            ctx.fillStyle = '#555';
            ctx.fillRect(18, 76 - legSwing, 18, 4);

            // 装饰
            if (type === 0) { ctx.fillStyle = 'rgba(139,90,43,0.3)';
                ctx.beginPath();
                ctx.moveTo(0, 28);
                ctx.quadraticCurveTo(-16, 44, -4, 64);
                ctx.fill(); }
            if (type === 2) { ctx.fillStyle = 'rgba(255,0,255,0.2)';
                ctx.beginPath();
                ctx.moveTo(36, 30);
                ctx.quadraticCurveTo(52, 46, 40, 66);
                ctx.fill(); }
            ctx.restore();
            ctx.globalAlpha = 1;
            ctx.shadowBlur = 0;
        }
        CanvasRenderingContext2D.prototype.roundRect = function(x, y, w, h, r) {
            if (r > w / 2) r = w / 2;
            if (r > h / 2) r = h / 2;
            this.moveTo(x + r, y);
            this.arcTo(x + w, y, x + w, y + h, r);
            this.arcTo(x + w, y + h, x, y + h, r);
            this.arcTo(x, y + h, x, y, r);
            this.arcTo(x, y, x + w, y, r);
            return this;
        };

        // ================================================================
        //  绘制敌人（精简版，保留视觉风格）
        // ================================================================
        function drawEnemy(ctx, e, level) {
            ctx.save();
            ctx.translate(e.x, e.y);
            const t = e.type;
            if (level === 1) {
                ctx.fillStyle = '#3CB371';
                ctx.fillRect(10, 18, 8, 30);
                const flowerGrad = ctx.createRadialGradient(14, 12, 4, 14, 16, 20);
                flowerGrad.addColorStop(0, '#FF6347');
                flowerGrad.addColorStop(1, '#8B0000');
                ctx.fillStyle = flowerGrad;
                ctx.beginPath();
                ctx.arc(14, 14, 20, 0, Math.PI * 2);
                ctx.fill();
                for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 + Date.now() * 0.0005;
                    ctx.fillStyle = '#FF4500';
                    ctx.shadowColor = '#FF4500';
                    ctx.shadowBlur = 10;
                    ctx.beginPath();
                    ctx.ellipse(14 + Math.cos(a) * 22, 14 + Math.sin(a) * 22, 8, 6, a, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.shadowBlur = 0; }
                ctx.fillStyle = '#FFD700';
                ctx.beginPath();
                ctx.arc(14, 14, 6, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#FFF';
                ctx.beginPath();
                ctx.arc(8, 10, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(20, 10, 5, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.arc(8, 10, 2.5, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(20, 10, 2.5, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#8B0000';
                ctx.fillRect(6, 18, 16, 6);
                for (let i = 0; i < 6; i++) { ctx.fillStyle = '#FFF';
                    ctx.fillRect(8 + i * 3, 16, 2, 6); }
            } else if (level === 2) {
                const bodyGrad = ctx.createLinearGradient(2, 10, 32, 40);
                bodyGrad.addColorStop(0, '#8A9BA8');
                bodyGrad.addColorStop(1, '#4A5A6A');
                ctx.fillStyle = bodyGrad;
                ctx.beginPath();
                ctx.ellipse(16, 24, 18, 16, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#A0B0C0';
                ctx.beginPath();
                ctx.moveTo(22, 8);
                ctx.lineTo(38, 16);
                ctx.lineTo(30, 24);
                ctx.closePath();
                ctx.fill();
                ctx.fillStyle = '#555';
                ctx.beginPath();
                ctx.moveTo(24, 2);
                ctx.lineTo(28, 10);
                ctx.lineTo(20, 10);
                ctx.closePath();
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo(34, 2);
                ctx.lineTo(38, 10);
                ctx.lineTo(30, 10);
                ctx.closePath();
                ctx.fill();
                ctx.shadowColor = '#FF0000';
                ctx.shadowBlur = 15;
                ctx.fillStyle = '#FF0000';
                ctx.beginPath();
                ctx.arc(28, 12, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(34, 12, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#4A5A6A';
                ctx.fillRect(4, 34, 5, 14);
                ctx.fillRect(12, 34, 5, 14);
                ctx.fillRect(22, 34, 5, 14);
                ctx.fillRect(30, 34, 5, 14);
                ctx.fillStyle = '#6A7B88';
                ctx.beginPath();
                ctx.moveTo(0, 22);
                ctx.quadraticCurveTo(-10, 12, -4, 6);
                ctx.lineTo(-2, 14);
                ctx.closePath();
                ctx.fill();
            } else if (level === 3) {
                for (let i = 0; i < 8; i++) {
                    const segGrad = ctx.createRadialGradient(i * 8 + 4, 14 + Math.sin(i * 0.7) * 4, 2, i * 8 + 4, 18 + Math
                        .sin(i * 0.7) * 4, 8);
                    segGrad.addColorStop(0, '#D2B48C');
                    segGrad.addColorStop(1, '#A08060');
                    ctx.fillStyle = segGrad;
                    ctx.beginPath();
                    ctx.ellipse(i * 8 + 4, 16 + Math.sin(i * 0.7) * 4, 6, 10, 0, 0, Math.PI * 2);
                    ctx.fill();
                }
                const headGrad = ctx.createRadialGradient(-4, 16, 2, -4, 16, 12);
                headGrad.addColorStop(0, '#C4A882');
                headGrad.addColorStop(1, '#8A7050');
                ctx.fillStyle = headGrad;
                ctx.beginPath();
                ctx.ellipse(-4, 16, 12, 14, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#000';
                ctx.beginPath();
                ctx.arc(-8, 12, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(-8, 20, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#8B0000';
                ctx.beginPath();
                ctx.arc(-4, 16, 6, 0, Math.PI);
                ctx.fill();
            } else if (level === 4) {
                const bodyGrad = ctx.createRadialGradient(16, 22, 6, 16, 28, 22);
                bodyGrad.addColorStop(0, '#F0F8FF');
                bodyGrad.addColorStop(1, '#B0C4DE');
                ctx.fillStyle = bodyGrad;
                ctx.beginPath();
                ctx.ellipse(16, 24, 18, 22, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#E8F0F8';
                ctx.beginPath();
                ctx.ellipse(16, 8, 14, 14, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowColor = '#00BFFF';
                ctx.shadowBlur = 20;
                ctx.fillStyle = '#0000FF';
                ctx.beginPath();
                ctx.arc(10, 8, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(22, 8, 4, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#ADD8E6';
                ctx.shadowColor = '#ADD8E6';
                ctx.shadowBlur = 10;
                ctx.beginPath();
                ctx.moveTo(4, -2);
                ctx.lineTo(8, -12);
                ctx.lineTo(12, -2);
                ctx.closePath();
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo(28, -2);
                ctx.lineTo(32, -12);
                ctx.lineTo(36, -2);
                ctx.closePath();
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#E8F0F8';
                ctx.fillRect(-8, 18, 8, 16);
                ctx.fillRect(32, 18, 8, 16);
            } else {
                const bodyGrad = ctx.createRadialGradient(16, 20, 4, 16, 28, 20);
                bodyGrad.addColorStop(0, '#FF6347');
                bodyGrad.addColorStop(1, '#8B0000');
                ctx.fillStyle = bodyGrad;
                ctx.beginPath();
                ctx.ellipse(16, 24, 18, 22, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = '#CC3300';
                ctx.beginPath();
                ctx.ellipse(16, 8, 12, 12, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowColor = '#FFD700';
                ctx.shadowBlur = 20;
                ctx.fillStyle = '#FFD700';
                ctx.beginPath();
                ctx.arc(10, 8, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.arc(22, 8, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#333';
                ctx.beginPath();
                ctx.moveTo(4, 0);
                ctx.lineTo(0, -14);
                ctx.lineTo(10, -4);
                ctx.closePath();
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo(28, 0);
                ctx.lineTo(32, -14);
                ctx.lineTo(22, -4);
                ctx.closePath();
                ctx.fill();
                const wingGrad = ctx.createRadialGradient(-6, 12, 2, -6, 12, 18);
                wingGrad.addColorStop(0, '#FF4500');
                wingGrad.addColorStop(1, 'rgba(255,0,0,0)');
                ctx.fillStyle = wingGrad;
                ctx.beginPath();
                ctx.moveTo(0, 12);
                ctx.quadraticCurveTo(-20, 0, -10, 24);
                ctx.closePath();
                ctx.fill();
                ctx.beginPath();
                ctx.moveTo(32, 12);
                ctx.quadraticCurveTo(52, 0, 42, 24);
                ctx.closePath();
                ctx.fill();
                ctx.fillStyle = '#8B0000';
                ctx.fillRect(0, 28, 8, 4);
                for (let i = 0; i < 3; i++) { ctx.fillRect(i * 3 - 2, 24, 2, 8); }
            }
            if (t === 2) { ctx.fillStyle = 'rgba(100,100,100,0.6)';
                ctx.strokeStyle = '#888';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.roundRect(-6, 8, 10, 24, 4);
                ctx.fill();
                ctx.stroke(); }
            ctx.restore();
            if (e.maxHp > 1) { ctx.fillStyle = '#333';
                ctx.fillRect(e.x, e.y - 12, e.w, 5);
                ctx.fillStyle = '#0F0';
                ctx.fillRect(e.x, e.y - 12, e.w * (e.hp / e.maxHp), 5); }
        }

        // ================================================================
        //  绘制 Boss
        // ================================================================
        function drawBoss(ctx, b) {
            ctx.save();
            ctx.translate(b.x, b.y);
            ctx.fillStyle = 'rgba(80,0,80,0.6)';
            ctx.beginPath();
            ctx.moveTo(0, 20);
            ctx.quadraticCurveTo(-30, 50, -10, 100);
            ctx.quadraticCurveTo(0, 90, 10, 100);
            ctx.closePath();
            ctx.fill();
            ctx.fillStyle = 'rgba(120,0,120,0.4)';
            ctx.beginPath();
            ctx.moveTo(80, 20);
            ctx.quadraticCurveTo(110, 50, 90, 100);
            ctx.quadraticCurveTo(80, 90, 70, 100);
            ctx.closePath();
            ctx.fill();
            const armorGrad = ctx.createLinearGradient(10, 20, 70, 90);
            armorGrad.addColorStop(0, '#7A7A9A');
            armorGrad.addColorStop(1, '#3A3A5A');
            ctx.fillStyle = armorGrad;
            ctx.beginPath();
            ctx.roundRect(10, 20, 60, 80, 6);
            ctx.fill();
            ctx.strokeStyle = 'rgba(200,200,255,0.2)';
            ctx.lineWidth = 1;
            for (let i = 0; i < 4; i++) { ctx.beginPath();
                ctx.moveTo(14, 30 + i * 18);
                ctx.lineTo(66, 30 + i * 18);
                ctx.stroke(); }
            ctx.fillStyle = '#FFD700';
            ctx.beginPath();
            ctx.roundRect(22, 30, 36, 22, 4);
            ctx.fill();
            ctx.fillStyle = '#FFFFAA';
            ctx.fillRect(28, 34, 24, 6);
            ctx.fillStyle = '#5A5A7A';
            ctx.fillRect(2, 16, 16, 10);
            ctx.fillRect(62, 16, 16, 10);
            ctx.fillStyle = '#FFD700';
            ctx.fillRect(4, 18, 12, 4);
            ctx.fillRect(64, 18, 12, 4);
            const headGrad = ctx.createRadialGradient(30, 6, 4, 40, 12, 16);
            headGrad.addColorStop(0, '#E8C9A0');
            headGrad.addColorStop(1, '#A08060');
            ctx.fillStyle = headGrad;
            ctx.beginPath();
            ctx.ellipse(40, 12, 20, 16, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#4A4A6A';
            ctx.fillRect(16, -6, 48, 14);
            ctx.fillRect(24, -18, 32, 14);
            ctx.fillStyle = '#FFD700';
            ctx.fillRect(24, -4, 32, 2);
            ctx.shadowColor = '#FF0000';
            ctx.shadowBlur = 35;
            ctx.fillStyle = '#FF0000';
            ctx.fillRect(26, 8, 10, 8);
            ctx.fillRect(44, 8, 10, 8);
            ctx.shadowBlur = 0;
            ctx.strokeStyle = '#4A2A2A';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(30, 22);
            ctx.lineTo(50, 22);
            ctx.stroke();
            ctx.fillStyle = '#3A3A5A';
            ctx.fillRect(22, 96, 16, 28);
            ctx.fillRect(42, 96, 16, 28);
            ctx.fillStyle = '#222';
            ctx.fillRect(18, 118, 22, 12);
            ctx.fillRect(40, 118, 22, 12);
            ctx.fillStyle = '#555';
            ctx.fillRect(16, 126, 26, 4);
            ctx.fillRect(38, 126, 26, 4);
            ctx.fillStyle = '#D2B48C';
            ctx.fillRect(66, 30, 16, 16);
            ctx.fillRect(74, 44, 8, 16);
            ctx.fillStyle = '#8B4513';
            ctx.fillRect(80, 24, 8, 20);
            ctx.fillStyle = '#FFD700';
            ctx.fillRect(82, 28, 4, 4);
            ctx.fillRect(82, 36, 4, 4);
            const bladeGrad = ctx.createLinearGradient(84, -40, 94, -40);
            bladeGrad.addColorStop(0, '#E0E0E0');
            bladeGrad.addColorStop(0.4, '#FFFFFF');
            bladeGrad.addColorStop(1, '#888888');
            ctx.shadowColor = '#FFFFFF';
            ctx.shadowBlur = 30;
            ctx.fillStyle = bladeGrad;
            ctx.fillRect(84, -40, 10, 68);
            ctx.shadowBlur = 0;
            ctx.shadowColor = '#00FFFF';
            ctx.shadowBlur = 15;
            ctx.fillStyle = '#00FFFF';
            ctx.fillRect(86, -30, 2, 8);
            ctx.fillRect(86, -14, 2, 8);
            ctx.fillRect(86, 2, 2, 8);
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#D2B48C';
            ctx.fillRect(-2, 34, 16, 16);
            ctx.fillRect(0, 48, 8, 14);
            ctx.fillStyle = '#4A4A6A';
            ctx.fillRect(78, 20, 14, 6);
            ctx.restore();
            ctx.fillStyle = '#333';
            ctx.fillRect(b.x, b.y - 30, b.w, 14);
            ctx.fillStyle = '#FF2222';
            ctx.fillRect(b.x, b.y - 30, b.w * (b.hp / b.maxHp), 14);
            ctx.fillStyle = '#FFD700';
            ctx.font = 'bold 26px sans-serif';
            ctx.fillText('自威', b.x + 16, b.y - 36);
        }

        // ----- 游戏逻辑函数 -----
        function buildLevel(level) {
            obstacles = [];
            enemies = [];
            enemyBullets = [];
            playerBullets = [];
            medicalItems = [];
            particles = [];
            slashEffects = [];
            boss = null;
            bossActive = false;
            flag = { x: LEVEL_WIDTH - 80, y: GROUND_Y - 100, w: 40, h: 100 };
            for (let i = 0; i < 14 + level * 3; i++) {
                let x = 200 + Math.random() * (LEVEL_WIDTH - 400),
                    w = 30 + Math.random() * 70,
                    h = 20 + Math.random() * 50,
                    y = GROUND_Y - h;
                let ok = true;
                for (let o of obstacles) { if (Math.abs(o.x - x) < 70 && Math.abs(o.y - y) < 70) { ok = false; break; } }
                if (ok) obstacles.push({ x, y, w, h, color: '#8B6B4A' });
            }
            for (let i = 0; i < 6 + level * 2; i++) {
                let x = 150 + Math.random() * (LEVEL_WIDTH - 300),
                    w = 60 + Math.random() * 100,
                    y = GROUND_Y - 100 - Math.random() * 180;
                obstacles.push({ x, y, w, h: 16, color: '#7A9A7A', isPlatform: true });
            }
            for (let i = 0; i < 4 + level; i++) {
                let x = 200 + Math.random() * (LEVEL_WIDTH - 400),
                    y = GROUND_Y - 34;
                medicalItems.push({ x, y, w: 24, h: 24, healAmount: 10 + Math.floor(Math.random() * 11) });
            }
            if (level < 5) {
                for (let i = 0; i < 6 + level * 3; i++) {
                    let x = 200 + Math.random() * (LEVEL_WIDTH - 400),
                        ok = true;
                    for (let o of obstacles) { if (Math.abs(o.x - x) < 60) { ok = false; break; } }
                    if (ok) {
                        let type = Math.floor(Math.random() * 3),
                            hp = type === 2 ? 2 : 1,
                            size = 30;
                        enemies.push({ x, y: GROUND_Y - size - 4, w: size, h: size + 6, vx: (Math.random() > 0.5 ? 1 :
                                -1) * (1.2 + level * 0.25), hp, maxHp: hp, shootTimer: 50 + Math.random() * 70,
                            type, onGround: true, level });
                    }
                }
            } else {
                boss = { x: LEVEL_WIDTH - 350, y: GROUND_Y - 150, w: 90, h: 150, hp: 40 + level * 6, maxHp: 40 + level *
                        6, shootTimer: 25, moveTimer: 0, vx: 0, vy: 0, slashCooldown: 0 };
                bossActive = true;
                for (let i = 0; i < 4; i++) { enemies.push({ x: 200 + Math.random() * 600, y: GROUND_Y - 34, w: 30,
                        h: 36, vx: (Math.random() > 0.5 ? 1 : -1) * 1.3, hp: 1, maxHp: 1, shootTimer: 40 + Math
                            .random() * 50, type: 0, onGround: true, level: 5 }); }
            }
            player.x = 120;
            player.y = GROUND_Y - 56;
            player.vx = 0;
            player.vy = 0;
            player.onGround = false;
            player.invincible = 90;
            player.dead = false;
            if (level > 1) player.hp = Math.min(player.hp + 20, MAX_HP);
            camera.x = 0;
        }

        function showLoading(cb) { gameState = 'LOADING';
            loadingProgress = 0;
            const itv = setInterval(() => { loadingProgress += 0.08; if (loadingProgress >= 1) { clearInterval(itv);
                    cb(); } }, 30); }

        function showTransition(level, skillText) { gameState = 'TRANSITION';
            transitionTimer = 120;
            transitionMessage = `第 ${level} 关 完成！`;
            if (skillText) { showSkillUnlock = true;
                skillUnlockText = skillText;
                skillUnlockTimer = 120; } else showSkillUnlock = false; }

        function startGame() {
            showLoading(() => {
                gameState = 'PLAYING';
                currentLevel = 1;
                score = 0;
                player.hp = MAX_HP;
                skills = { doubleJump: false, dash: false, shield: false, attackUp: false, rapidFire: false,
                    bulletPenetrate: false, bulletSplit: false };
                player.attackPower = 2;
                player.baseShootCooldown = 8;
                shieldTimer = 0;
                buildLevel(currentLevel);
            });
        }

        function resetGame() {
            gameState = 'MENU';
            selectedHero = 0;
            currentLevel = 1;
            score = 0;
            player.hp = MAX_HP;
            skills = { doubleJump: false, dash: false, shield: false, attackUp: false, rapidFire: false,
                bulletPenetrate: false, bulletSplit: false };
            player.attackPower = 2;
            player.baseShootCooldown = 8;
            boss = null;
            bossActive = false;
            enemies = [];
            playerBullets = [];
            enemyBullets = [];
            obstacles = [];
            medicalItems = [];
            particles = [];
            slashEffects = [];
            flag = null;
            player.x = 120;
            player.y = GROUND_Y - 56;
        }

        function completeLevel() {
            if (currentLevel === MAX_LEVEL) { gameState = 'WIN'; return; }
            let skillText = '';
            if (currentLevel === 1) { skills.attackUp = true;
                player.attackPower = 3;
                skillText = '攻击强化：伤害+1'; } else if (currentLevel === 2) { skills.rapidFire = true;
                player.baseShootCooldown = 5;
                skillText = '速射：射速提升'; } else if (currentLevel === 3) { skills.bulletPenetrate = true;
                skillText = '穿透弹：子弹穿透一个敌人'; } else if (currentLevel === 4) { skills.bulletSplit = true;
                skillText = '分裂弹：命中后分裂'; }
            if (currentLevel === 1) { skills.doubleJump = true;
                skillText += '，二段跳'; }
            if (currentLevel === 2) { skills.dash = true;
                skillText += '，冲刺'; }
            if (currentLevel === 3) { skills.shield = true;
                skillText += '，护盾'; }
            showTransition(currentLevel, skillText);
            currentLevel++;
            setTimeout(() => {
                showLoading(() => {
                    gameState = 'PLAYING';
                    buildLevel(currentLevel);
                    if (currentLevel === 5) transitionMessage = '⚠️ Boss 战！击败 自威！';
                });
            }, 2200);
        }

        function hurtPlayer(damage = 5) {
            if (player.invincible > 0 || shieldTimer > 0 || player.dead) return;
            player.hp -= damage;
            if (player.hp <= 0) { player.hp = 0;
                gameState = 'GAMEOVER';
                player.dead = true; return; }
            player.invincible = 60;
            player.vx = (player.facing === 1 ? -6 : 6);
            player.vy = -4;
        }

        // ----- 更新逻辑（整合触摸）-----
        function update() {
            if (gameState === 'TRANSITION') { transitionTimer--; if (showSkillUnlock) skillUnlockTimer--; return; }
            if (gameState !== 'PLAYING') return;
            frameCount++;

            // 冷却
            if (player.shootCooldown > 0) player.shootCooldown--;
            if (player.invincible > 0) player.invincible--;
            if (player.dashCooldown > 0) player.dashCooldown--;
            if (shieldTimer > 0) shieldTimer--;
            if (player.isDashing) { player.dashTimer--; if (player.dashTimer <= 0) player.isDashing = false; }

            // ---- 触摸移动控制 ----
            let moveX = 0;
            if (touch.leftActive) {
                // 计算滑动方向：相对于屏幕中心
                const centerX = canvas.width * 0.225;
                const dx = touch.leftX - centerX;
                if (Math.abs(dx) > 15) {
                    moveX = dx > 0 ? 1 : -1;
                }
                // 上滑跳跃（快速向上滑动）
                if (touch.leftY < canvas.height * 0.25) {
                    if (player.onGround) { player.vy = JUMP_FORCE;
                        player.onGround = false;
                        player.hasDoubleJumped = false; } else if (skills.doubleJump && !player.hasDoubleJumped &&
                        player.vy > -2) { player.vy = JUMP_FORCE * 0.9;
                        player.hasDoubleJumped = true;
                        spawnParticles(player.x + player.w / 2, player.y + player.h, '#88FFFF', 16, 5); }
                }
            }

            // 键盘兼容
            if (keys.a) moveX = -1;
            if (keys.d) moveX = 1;

            if (moveX !== 0) player.facing = moveX;
            if (moveX !== 0 && player.onGround) player.walkCycle += 0.18;
            else player.walkCycle *= 0.9;

            // ---- 跳跃按钮 ----
            if (touch.jumpPressed || keys.w || keys.space) {
                if (player.onGround) { player.vy = JUMP_FORCE;
                    player.onGround = false;
                    player.hasDoubleJumped = false; } else if (skills.doubleJump && !player.hasDoubleJumped && player
                    .vy > -2) { player.vy = JUMP_FORCE * 0.9;
                    player.hasDoubleJumped = true;
                    spawnParticles(player.x + player.w / 2, player.y + player.h, '#88FFFF', 16, 5); }
            }

            // ---- 冲刺 ----
            if ((touch.dashPressed || keys.shift) && skills.dash && player.dashCooldown === 0 && moveX !== 0 && !player
                .isDashing) {
                player.isDashing = true;
                player.dashTimer = 12;
                player.dashCooldown = 40;
                player.vx = moveX * 16;
                spawnParticles(player.x + player.w / 2, player.y + player.h / 2, '#FFAA00', 15, 6);
            }

            // ---- 物理 ----
            if (!player.isDashing) player.vx = moveX * PLAYER_SPEED;
            player.vy += GRAVITY;
            if (player.vy > 16) player.vy = 16;
            player.x += player.vx;
            player.y += player.vy;

            if (player.y + player.h >= GROUND_Y) { player.y = GROUND_Y - player.h;
                player.vy = 0;
                player.onGround = true;
                player.hasDoubleJumped = false; } else player.onGround = false;

            // 障碍物碰撞
            for (let o of obstacles) {
                if (rectCollide({ x: player.x, y: player.y, w: player.w, h: player.h }, { x: o.x, y: o.y, w: o.w, h: o
                            .h })) {
                    if (player.vy > 0 && player.y + player.h - player.vy <= o.y + 6) { player.y = o.y - player.h;
                        player.vy = 0;
                        player.onGround = true;
                        player.hasDoubleJumped = false; } else if (player.vy < 0 && player.y - player.vy >= o.y + o
                        .h - 6) { player.y = o.y + o.h;
                        player.vy = 0; } else { if (player.vx > 0) player.x = o.x - player.w;
                        else if (player.vx < 0) player.x = o.x + o.w;
                        player.vx = 0; }
                }
            }
            if (player.x < 0) player.x = 0;
            if (player.x + player.w > LEVEL_WIDTH) player.x = LEVEL_WIDTH - player.w;

            // ---- 护盾 ----
            if ((touch.shieldPressed || keys.e) && skills.shield && shieldTimer === 0) {
                shieldTimer = 200;
                spawnParticles(player.x + player.w / 2, player.y + player.h / 2, '#00FFFF', 30, 8);
            }

            // ---- 射击（触摸右侧瞄准 + 按钮）----
            let shouldShoot = touch.shootPressed || keys.mouseLeft;
            if (shouldShoot && player.shootCooldown === 0) {
                let targetX = mouseX + camera.x;
                let targetY = mouseY;
                if (touch.rightActive) {
                    targetX = touch.rightX + camera.x;
                    targetY = touch.rightY;
                }
                const dx = targetX - (player.x + player.w / 2);
                const dy = targetY - (player.y + player.h / 2);
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist > 10) {
                    const spd = 13,
                        dmg = player.attackPower,
                        vx = (dx / dist) * spd,
                        vy = (dy / dist) * spd;
                    playerBullets.push({ x: player.x + player.w / 2 - 7, y: player.y + player.h / 2 - 4, w: 14, h: 8,
                        vx, vy, damage: dmg, penetrate: skills.bulletPenetrate ? 1 : 0, split: skills
                            .bulletSplit });
                    spawnParticles(player.x + player.w / 2, player.y + player.h / 2, '#FFD700', 12, 4, 4);
                }
                player.shootCooldown = player.baseShootCooldown;
            }

            // ---- 子弹更新 ----
            for (let i = playerBullets.length - 1; i >= 0; i--) {
                const b = playerBullets[i];
                b.x += b.vx;
                b.y += b.vy;
                let hit = false;
                for (let o of obstacles) {
                    if (rectCollide({ x: b.x, y: b.y, w: b.w, h: b.h }, { x: o.x, y: o.y, w: o.w, h: o.h })) { hit =
                            true;
                        spawnParticles(b.x + b.w / 2, b.y + b.h / 2, '#FFAA44', 12, 5); break; }
                }
                if (hit || b.x > LEVEL_WIDTH + 60 || b.x < -60 || b.y > H + 60 || b.y < -60) playerBullets.splice(i,
                1);
            }
            for (let i = enemyBullets.length - 1; i >= 0; i--) {
                const b = enemyBullets[i];
                b.x += b.vx;
                b.y += b.vy;
                let hit = false;
                for (let o of obstacles) {
                    if (rectCollide({ x: b.x, y: b.y, w: b.w, h: b.h }, { x: o.x, y: o.y, w: o.w, h: o.h })) { hit =
                            true;
                        spawnParticles(b.x + b.w / 2, b.y + b.h / 2, '#FF4444', 8, 4); break; }
                }
                if (hit || b.x > LEVEL_WIDTH + 60 || b.x < -60 || b.y > H + 60 || b.y < -60) enemyBullets.splice(i,
                1);
            }

            // ---- 医疗箱 ----
            for (let i = medicalItems.length - 1; i >= 0; i--) {
                const med = medicalItems[i];
                if (rectCollide({ x: player.x, y: player.y, w: player.w, h: player.h }, { x: med.x, y: med.y, w: med
                            .w, h: med.h })) {
                    player.hp = Math.min(player.hp + med.healAmount, MAX_HP);
                    spawnParticles(med.x + 12, med.y + 12, '#00FF88', 30, 8);
                    medicalItems.splice(i, 1);
                }
            }

            // ---- 敌人 AI ----
            for (let i = enemies.length - 1; i >= 0; i--) {
                const e = enemies[i];
                e.x += e.vx;
                if (e.x < 50 || e.x > LEVEL_WIDTH - 50) e.vx *= -1;
                e.shootTimer--;
                if (e.shootTimer <= 0 && Math.abs(e.x - player.x) < 700) {
                    const dx = player.x - e.x,
                        dy = player.y - e.y,
                        dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist > 10) {
                        const spd = 3 + currentLevel * 0.35;
                        enemyBullets.push({ x: e.x + (dx < 0 ? -12 : e.w + 12), y: e.y + e.h / 2 - 5, w: 12, h: 12,
                            vx: (dx / dist) * spd, vy: (dy / dist) * spd });
                    }
                    e.shootTimer = 45 + Math.random() * 45;
                }
                if (!player.dead && rectCollide({ x: player.x, y: player.y, w: player.w, h: player.h }, { x: e.x, y: e
                            .y, w: e.w, h: e.h })) { hurtPlayer(5);
                    enemies.splice(i, 1); continue; }
                let killed = false;
                for (let j = playerBullets.length - 1; j >= 0; j--) {
                    const b = playerBullets[j];
                    if (rectCollide({ x: b.x, y: b.y, w: b.w, h: b.h }, { x: e.x, y: e.y, w: e.w, h: e.h })) {
                        if (b.penetrate > 0) {
                            b.penetrate--;
                            e.hp -= b.damage;
                            if (b.split) {
                                const a1 = Math.atan2(b.vy, b.vx) + 0.6,
                                    a2 = Math.atan2(b.vy, b.vx) - 0.6,
                                    sp = Math.sqrt(b.vx * b.vx + b.vy * b.vy);
                                playerBullets.push({ x: b.x, y: b.y, w: b.w, h: b.h, vx: Math.cos(a1) * sp, vy: Math
                                        .sin(a1) * sp, damage: b.damage, penetrate: 0, split: false });
                                playerBullets.push({ x: b.x, y: b.y, w: b.w, h: b.h, vx: Math.cos(a2) * sp, vy: Math
                                        .sin(a2) * sp, damage: b.damage, penetrate: 0, split: false });
                            }
                            if (e.hp <= 0) { killed = true;
                                spawnParticles(e.x + e.w / 2, e.y + e.h / 2, '#FF8800', 35, 9);
                                score += 15; if (Math.random() < 0.18) medicalItems.push({ x: e.x + e.w / 2 - 12,
                                    y: e.y - 24, w: 24, h: 24, healAmount: 12 + Math.floor(Math.random() *
                                        12) });
                                enemies.splice(i, 1); }
                            break;
                        } else {
                            playerBullets.splice(j, 1);
                            e.hp -= b.damage;
                            if (e.hp <= 0) { killed = true;
                                spawnParticles(e.x + e.w / 2, e.y + e.h / 2, '#FF8800', 35, 9);
                                score += 15; if (Math.random() < 0.18) medicalItems.push({ x: e.x + e.w / 2 - 12,
                                    y: e.y - 24, w: 24, h: 24, healAmount: 12 + Math.floor(Math.random() *
                                        12) });
                                enemies.splice(i, 1); }
                            break;
                        }
                    }
                }
                if (killed) continue;
                if (e.y > H + 60) enemies.splice(i, 1);
            }

            // ---- Boss ----
            if (bossActive && boss) {
                const b = boss;
                b.moveTimer--;
                if (b.moveTimer <= 0) { b.vx = (Math.random() - 0.5) * 4.5;
                    b.vy = (Math.random() - 0.5) * 3;
                    b.moveTimer = 30 + Math.random() * 40; if (b.x < 120) b.vx = Math.abs(b.vx); if (b.x + b.w >
                        LEVEL_WIDTH - 120) b.vx = -Math.abs(b.vx); if (b.y < 50) b.vy = Math.abs(b.vy); if (b.y +
                        b.h > GROUND_Y - 10) b.vy = -Math.abs(b.vy); }
                b.x += b.vx;
                b.y += b.vy;
                b.x = Math.max(100, Math.min(LEVEL_WIDTH - b.w - 100, b.x));
                b.y = Math.max(30, Math.min(GROUND_Y - b.h, b.y));
                b.slashCooldown--;
                if (b.slashCooldown <= 0 && Math.abs(b.x - player.x) < 550) {
                    const dx = player.x - (b.x + b.w / 2),
                        dy = player.y - (b.y + b.h / 2),
                        dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist > 20) {
                        const spd = 7;
                        slashEffects.push({ x: b.x + b.w, y: b.y + b.h / 2 - 12, w: 50, h: 24, vx: (dx / dist) *
                                spd, vy: (dy / dist) * spd, life: 35, maxLife: 35 });
                        spawnParticles(b.x + b.w, b.y + b.h / 2, '#FF8800', 20, 7);
                    }
                    b.slashCooldown = 22 + Math.random() * 18;
                }
                b.shootTimer--;
                if (b.shootTimer <= 0) {
                    for (let ang = -0.5; ang <= 0.5; ang += 0.5) {
                        const dx = player.x - b.x,
                            dy = player.y - b.y,
                            dist = Math.sqrt(dx * dx + dy * dy);
                        if (dist < 20) continue;
                        const spd = 5 + currentLevel * 0.2;
                        enemyBullets.push({ x: b.x + b.w / 2 - 7, y: b.y + b.h / 2 - 7, w: 14, h: 14, vx: Math.cos(
                                Math.atan2(dy, dx) + ang) * spd, vy: Math.sin(Math.atan2(dy, dx) + ang) *
                            spd });
                    }
                    b.shootTimer = 22 + Math.random() * 18;
                }
                if (!player.dead && rectCollide({ x: player.x, y: player.y, w: player.w, h: player.h }, { x: b.x, y: b
                            .y, w: b.w, h: b.h })) hurtPlayer(6);
                for (let j = playerBullets.length - 1; j >= 0; j--) {
                    const bul = playerBullets[j];
                    if (rectCollide({ x: bul.x, y: bul.y, w: bul.w, h: bul.h }, { x: b.x, y: b.y, w: b.w, h: b.h })) {
                        playerBullets.splice(j, 1);
                        b.hp -= bul.damage;
                        spawnParticles(bul.x + bul.w / 2, bul.y + bul.h / 2, '#FF00FF', 20, 7);
                        if (b.hp <= 0) {
                            spawnParticles(b.x + b.w / 2, b.y + b.h / 2, '#FF5500', 60, 12);
                            score += 150;
                            boss = null;
                            bossActive = false;
                            completeLevel();
                        }
                    }
                }
                for (let j = enemyBullets.length - 1; j >= 0; j--) {
                    const bul = enemyBullets[j];
                    if (rectCollide({ x: player.x, y: player.y, w: player.w, h: player.h }, { x: bul.x, y: bul.y, w: bul
                                .w, h: bul.h })) { enemyBullets.splice(j, 1);
                        hurtPlayer(5); break; }
                }
                for (let j = slashEffects.length - 1; j >= 0; j--) {
                    const sl = slashEffects[j];
                    if (rectCollide({ x: player.x, y: player.y, w: player.w, h: player.h }, { x: sl.x, y: sl.y, w: sl
                                .w, h: sl.h })) { slashEffects.splice(j, 1);
                        hurtPlayer(8); break; }
                }
            }

            for (let i = enemyBullets.length - 1; i >= 0; i--) {
                const b = enemyBullets[i];
                if (rectCollide({ x: player.x, y: player.y, w: player.w, h: player.h }, { x: b.x, y: b.y, w: b.w, h: b
                            .h })) { enemyBullets.splice(i, 1);
                    hurtPlayer(5); break; }
            }

            if (flag && !bossActive) {
                if (player.x + player.w > flag.x && player.y + player.h > flag.y) completeLevel();
            }

            for (let i = slashEffects.length - 1; i >= 0; i--) {
                const s = slashEffects[i];
                s.x += s.vx;
                s.y += s.vy;
                s.life--;
                if (s.life <= 0 || s.x > LEVEL_WIDTH + 60 || s.x < -60 || s.y > H + 60 || s.y < -60) slashEffects
                    .splice(i, 1);
            }
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.1;
                p.life--;
                if (p.life <= 0) particles.splice(i, 1);
            }

            let targetCamX = player.x - W * 0.35;
            targetCamX = Math.max(0, Math.min(targetCamX, LEVEL_WIDTH - W));
            camera.x += (targetCamX - camera.x) * 0.12;
            if (player.x < camera.x + 30) player.x = camera.x + 30;
            if (player.x + player.w > camera.x + W - 30) player.x = camera.x + W - 30 - player.w;
        }

        // ----- 绘制（手机适配）-----
        function draw() {
            ctx.clearRect(0, 0, W, H);
            const level = currentLevel;
            let bgColors, groundColor, treeColor, cloudColor, particleColor;
            if (level === 1) { bgColors = ['#0B2A1A', '#1A4A2A', '#2A5A3A'];
                groundColor = '#2D4A2D';
                treeColor = '#1E4A1E';
                cloudColor = 'rgba(200,240,200,0.08)';
                particleColor = '#88FF88'; } else if (level === 2) { bgColors = ['#1A0A0A', '#2A1A1A', '#3A2A2A'];
                groundColor = '#3A2A2A';
                treeColor = '#2A1A1A';
                cloudColor = 'rgba(100,80,80,0.05)';
                particleColor = '#FF8866'; } else if (level === 3) { bgColors = ['#4A3A1A', '#5A4A2A', '#6A5A3A'];
                groundColor = '#6A5A3A';
                treeColor = '#4A3A1A';
                cloudColor = 'rgba(255,240,200,0.06)';
                particleColor = '#FFDD88'; } else if (level === 4) { bgColors = ['#2A3A4A', '#3A4A5A', '#4A5A6A'];
                groundColor = '#E0E8F0';
                treeColor = '#C0D0E0';
                cloudColor = 'rgba(255,255,255,0.1)';
                particleColor = '#CCEEFF'; } else { bgColors = ['#2A0A0A', '#3A1A0A', '#4A2A0A'];
                groundColor = '#3A1A0A';
                treeColor = '#2A0A0A';
                cloudColor = 'rgba(255,100,50,0.08)';
                particleColor = '#FF6633'; }
            const grad = ctx.createLinearGradient(0, 0, 0, GROUND_Y);
            grad.addColorStop(0, bgColors[0]);
            grad.addColorStop(0.5, bgColors[1]);
            grad.addColorStop(1, bgColors[2]);
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, W, GROUND_Y);
            // 背景粒子
            for (let i = 0; i < 25; i++) { const x = (i * 73 + frameCount * 0.2) % W,
                    y = (i * 47 + Math.sin(i + frameCount * 0.01) * 30) % GROUND_Y;
                ctx.fillStyle = particleColor;
                ctx.globalAlpha = 0.3 + Math.sin(frameCount * 0.02 + i) * 0.2;
                ctx.beginPath();
                ctx.arc(x, y, 2 + Math.sin(i) * 1, 0, Math.PI * 2);
                ctx.fill(); }
            ctx.globalAlpha = 1;
            // 远山
            ctx.save();
            ctx.translate(-camera.x * 0.2, 0);
            ctx.fillStyle = treeColor;
            ctx.globalAlpha = 0.25;
            for (let i = 0; i < 25; i++) { let x = i * 220 + (level * 120);
                let y = GROUND_Y - 100 - Math.sin(i * 0.5 + level) * 70;
                ctx.beginPath();
                ctx.moveTo(x, y);
                ctx.lineTo(x + 40, y - 60);
                ctx.lineTo(x + 80, y);
                ctx.fill(); }
            ctx.globalAlpha = 1;
            ctx.restore();
            ctx.fillStyle = cloudColor;
            for (let i = 0; i < 12; i++) { let cx = (i * 160 + camera.x * 0.04) % (W + 240) - 120;
                let cy = 30 + i * 18 + Math.sin(i) * 20;
                ctx.beginPath();
                ctx.arc(cx, cy, 60 + i * 10, 0, Math.PI * 2);
                ctx.fill(); }

            ctx.save();
            ctx.translate(-camera.x, 0);
            ctx.fillStyle = groundColor;
            ctx.fillRect(0, GROUND_Y, LEVEL_WIDTH, H - GROUND_Y);
            ctx.fillStyle = (level === 4) ? '#C0D0E0' : '#1E3A1E';
            ctx.fillRect(0, GROUND_Y + 8, LEVEL_WIDTH, 6);
            ctx.strokeStyle = '#4A7A4A';
            ctx.lineWidth = 2;
            for (let i = 0; i < 200; i++) { const gx = (i * 30 + camera.x * 0.1) % LEVEL_WIDTH;
                ctx.beginPath();
                ctx.moveTo(gx, GROUND_Y - 2);
                ctx.lineTo(gx + 2, GROUND_Y - 10);
                ctx.stroke(); }
            for (let o of obstacles) {
                ctx.fillStyle = o.color || '#8B6B4A';
                if (o.isPlatform) { ctx.fillStyle = (level === 4) ? '#C0D0E0' : '#5A7A5A';
                    ctx.fillRect(o.x, o.y, o.w, o.h);
                    ctx.fillStyle = '#7A9A7A';
                    ctx.fillRect(o.x, o.y + o.h - 4, o.w, 4); } else { ctx.fillRect(o.x, o.y, o.w, o.h);
                    ctx.strokeStyle = '#5A4A3A';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(o.x, o.y, o.w, o.h); }
            }
            for (let med of medicalItems) {
                ctx.shadowColor = '#FF3344';
                ctx.shadowBlur = 25;
                ctx.fillStyle = '#FF3344';
                ctx.fillRect(med.x, med.y, med.w, med.h);
                ctx.fillStyle = '#FFF';
                ctx.font = '18px sans-serif';
                ctx.fillText('+', med.x + 6, med.y + 18);
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#FFF';
                ctx.font = '12px monospace';
                ctx.fillText(med.healAmount, med.x + 2, med.y - 6);
            }
            if (flag) {
                ctx.fillStyle = '#8B4513';
                ctx.fillRect(flag.x, flag.y, 8, flag.h);
                ctx.fillStyle = '#FF4444';
                ctx.beginPath();
                ctx.moveTo(flag.x + 8, flag.y);
                ctx.lineTo(flag.x + 40, flag.y + 25);
                ctx.lineTo(flag.x + 8, flag.y + 50);
                ctx.fill();
                ctx.fillStyle = '#FFD700';
                ctx.font = 'bold 28px sans-serif';
                ctx.fillText('🏁', flag.x - 12, flag.y - 12);
            }
            for (let p of particles) { ctx.globalAlpha = p.life / p.maxLife;
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x, p.y, p.size, p.size); }
            ctx.globalAlpha = 1;
            for (let e of enemies) drawEnemy(ctx, e, e.level || currentLevel);
            if (boss) drawBoss(ctx, boss);
            for (let s of slashEffects) {
                ctx.shadowColor = '#FF4400';
                ctx.shadowBlur = 40;
                ctx.fillStyle = 'rgba(255,68,0,0.7)';
                ctx.fillRect(s.x, s.y, s.w, s.h);
                ctx.fillStyle = 'rgba(255,200,0,0.4)';
                ctx.fillRect(s.x + 12, s.y - 6, s.w - 24, s.h + 12);
                ctx.shadowBlur = 0;
            }
            ctx.fillStyle = '#FFD700';
            ctx.shadowColor = '#FFD700';
            ctx.shadowBlur = 25;
            for (let b of playerBullets) ctx.fillRect(b.x, b.y, b.w, b.h);
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#FF4444';
            ctx.shadowColor = '#FF0000';
            ctx.shadowBlur = 20;
            for (let b of enemyBullets) { ctx.beginPath();
                ctx.arc(b.x + 6, b.y + 6, 8, 0, Math.PI * 2);
                ctx.fill(); }
            ctx.shadowBlur = 0;
            drawPlayer(ctx, player.x, player.y, selectedHero, player.facing, player.invincible > 0, shieldTimer > 0);
            ctx.restore();

            // HUD
            ctx.fillStyle = 'rgba(0,0,0,0.6)';
            ctx.fillRect(16, 40, 200, 20);
            ctx.fillStyle = player.hp > 50 ? '#00FF00' : (player.hp > 25 ? '#FFAA00' : '#FF0000');
            ctx.fillRect(18, 42, 196 * (player.hp / MAX_HP), 16);
            ctx.strokeStyle = '#FFF';
            ctx.lineWidth = 2;
            ctx.strokeRect(16, 40, 200, 20);
            ctx.fillStyle = '#FFF';
            ctx.font = 'bold 14px monospace';
            ctx.fillText(`HP ${player.hp}/${MAX_HP}`, 22, 56);
            ctx.shadowColor = 'black';
            ctx.shadowBlur = 10;
            ctx.fillStyle = '#FFF';
            ctx.font = 'bold 18px "Courier New"';
            ctx.fillText(`🏆 ${currentLevel}/${MAX_LEVEL}`, 230, 60);
            ctx.fillText(`⭐ ${score}`, 380, 60);
            if (shieldTimer > 0) { ctx.fillStyle = '#00FFFF';
                ctx.fillText('🛡️', 530, 60); }
            ctx.shadowBlur = 0;

            if (gameState === 'LOADING') {
                ctx.fillStyle = 'rgba(0,0,0,0.85)';
                ctx.fillRect(0, 0, W, H);
                ctx.fillStyle = '#FFF';
                ctx.font = 'bold 48px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('加载中...', W / 2, 260);
                ctx.fillStyle = '#555';
                ctx.fillRect(W / 2 - 220, 310, 440, 36);
                ctx.fillStyle = '#0CF';
                ctx.fillRect(W / 2 - 220, 310, 440 * loadingProgress, 36);
                ctx.textAlign = 'left';
            }
            if (gameState === 'TRANSITION') {
                ctx.fillStyle = 'rgba(0,0,0,0.75)';
                ctx.fillRect(0, 0, W, H);
                ctx.textAlign = 'center';
                ctx.fillStyle = '#FFD700';
                ctx.font = 'bold 46px sans-serif';
                ctx.fillText(transitionMessage, W / 2, 200);
                if (showSkillUnlock && skillUnlockTimer > 0) {
                    ctx.fillStyle = '#00FF88';
                    ctx.font = 'bold 30px sans-serif';
                    ctx.fillText('✨ 技能解锁：' + skillUnlockText, W / 2, 280);
                }
                ctx.textAlign = 'left';
            }
            if (gameState === 'MENU') drawMenu();
            if (gameState === 'GAMEOVER') {
                ctx.fillStyle = 'rgba(0,0,0,0.9)';
                ctx.fillRect(0, 0, W, H);
                ctx.textAlign = 'center';
                ctx.fillStyle = '#FF2222';
                ctx.font = 'bold 70px "Courier New"';
                ctx.shadowColor = '#FF0000';
                ctx.shadowBlur = 50;
                ctx.fillText('💀 失败', W / 2, 200);
                ctx.shadowBlur = 0;
                const taunt = taunts[Math.floor(Math.random() * taunts.length)];
                ctx.fillStyle = '#FFAA88';
                ctx.font = 'bold 36px sans-serif';
                ctx.fillText(taunt, W / 2, 290);
                ctx.fillStyle = '#FFF';
                ctx.font = '28px "Courier New"';
                ctx.fillText('按 R 重新挑战', W / 2, 370);
                ctx.textAlign = 'left';
            }
            if (gameState === 'WIN') {
                ctx.fillStyle = 'rgba(0,0,0,0.9)';
                ctx.fillRect(0, 0, W, H);
                ctx.textAlign = 'center';
                ctx.fillStyle = '#FFD700';
                ctx.font = 'bold 64px "Courier New"';
                ctx.shadowColor = '#FFD700';
                ctx.shadowBlur = 50;
                ctx.fillText('🎉 拯救成功！', W / 2, 180);
                ctx.fillStyle = '#FFAACC';
                ctx.font = 'bold 42px sans-serif';
                ctx.fillText('✨ 男娘 · 精扬 ✨', W / 2, 270);
                ctx.shadowBlur = 0;
                ctx.fillStyle = '#FFF';
                ctx.font = '30px "Courier New"';
                ctx.fillText(`最终得分: ${score}  ·  按 R 重玩`, W / 2, 370);
                ctx.textAlign = 'left';
            }

            // 触摸控制提示（只显示一次）
            if (frameCount < 180 && gameState === 'PLAYING') {
                ctx.fillStyle = 'rgba(0,0,0,0.5)';
                ctx.fillRect(10, H - 50, 300, 40);
                ctx.fillStyle = '#FFF';
                ctx.font = '14px sans-serif';
                ctx.fillText('←左滑移动 · 右滑瞄准 · 按钮射击→', 20, H - 22);
            }
        }

        function drawMenu() {
            ctx.fillStyle = 'rgba(8,8,24,0.94)';
            ctx.fillRect(0, 0, W, H);
            ctx.textAlign = 'center';
            ctx.fillStyle = '#FFD700';
            ctx.font = 'bold 50px "Courier New"';
            ctx.shadowColor = '#FFD700';
            ctx.shadowBlur = 40;
            ctx.fillText('⚔️ 魂斗罗 · 手机版 ⚔️', W / 2, 100);
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#AAA';
            ctx.font = '20px "Courier New"';
            ctx.fillText('5关 · 触摸控制 · Boss持刀 · 救男娘', W / 2, 150);
            const heroes = [{ id: 0, name: '烧哲', style: '🤠 西部牛仔', color: '#CD853F' }, { id: 1, name: '俊子',
                    style: '🎖️ 现代士兵', color: '#6B8E23' }, { id: 2, name: '德育月', style: '🤖 赛博朋克',
                    color: '#DA70D6' }];
            const startX = 140,
                boxW = 260,
                gap = 50,
                y = 200,
                boxH = 260;
            for (let i = 0; i < 3; i++) {
                const x = startX + i * (boxW + gap);
                const h = heroes[i];
                ctx.shadowBlur = 25;
                ctx.shadowColor = h.color;
                ctx.fillStyle = (selectedHero === i) ? '#222266' : '#1A1A2E';
                ctx.strokeStyle = (selectedHero === i) ? h.color : '#555';
                ctx.lineWidth = (selectedHero === i) ? 6 : 2;
                ctx.fillRect(x, y, boxW, boxH);
                ctx.strokeRect(x, y, boxW, boxH);
                ctx.shadowBlur = 0;
                ctx.save();
                ctx.translate(x + boxW / 2 - 24, y + 40);
                drawPlayer(ctx, 0, 0, i, 1, false, false);
                ctx.restore();
                ctx.fillStyle = '#FFF';
                ctx.font = 'bold 28px "Courier New"';
                ctx.fillText(h.name, x + boxW / 2, y + 170);
                ctx.fillStyle = h.color;
                ctx.font = '18px "Courier New"';
                ctx.fillText(h.style, x + boxW / 2, y + 210);
                ctx.fillStyle = '#888';
                ctx.font = '18px "Courier New"';
                ctx.fillText(`[ ${i+1} ]`, x + boxW / 2, y + 245);
            }
            ctx.fillStyle = '#667';
            ctx.font = '16px "Courier New"';
            ctx.fillText('← 触摸屏幕左侧移动 · 右侧瞄准 · 按钮操作 →', W / 2, 500);
            ctx.textAlign = 'left';
        }

        // ----- 游戏循环 -----
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }
        gameLoop();

        // 点击菜单选人（手机兼容）
        canvas.addEventListener('click', (e) => {
            if (gameState !== 'MENU') return;
            const rect = canvas.getBoundingClientRect();
            const sx = canvas.width / rect.width,
                sy = canvas.height / rect.height;
            const mx = (e.clientX - rect.left) * sx,
                my = (e.clientY - rect.top) * sy;
            const startX = 140,
                boxW = 260,
                gap = 50,
                y = 200,
                boxH = 260;
            for (let i = 0; i < 3; i++) {
                const x = startX + i * (boxW + gap);
                if (mx > x && mx < x + boxW && my > y && my < y + boxH) { selectedHero = i;
                    startGame(); break; }
            }
        });
    </script>
</body>
</html>
