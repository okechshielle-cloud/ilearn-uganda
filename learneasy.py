import streamlit as st

st.set_page_config(page_title="iLearn-Uganda - 3D Omweso", layout="centered")

st.title("🎲 iLearn-Uganda: 3D Animated Omweso")
st.caption("Traditional Ugandan Board Game with 3D Physics Sowing & Audio Cues")

# We embed a fully self-contained HTML5/JS application with 3D canvas rendering and Web Audio sound synthesis
omweso_html = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {
    background: #2b1810;
    color: #f4e8d8;
    font-family: sans-serif;
    text-align: center;
    margin: 0;
    padding: 10px;
  }
  #board-container {
    background: linear-data(135deg, #5c2c16, #3a1a0b);
    border: 6px solid #8B4513;
    border-radius: 16px;
    padding: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.6);
    display: inline-block;
    max-width: 650px;
    width: 100%;
  }
  .row {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin: 10px 0;
  }
  .pit {
    width: 55px;
    height: 70px;
    background: radial-gradient(circle at 50% 30%, #1e0d05, #0f0502);
    border: 3px solid #d4a373;
    border-radius: 50%/30%;
    box-shadow: inset 0 8px 12px rgba(0,0,0,0.9), 0 3px 6px rgba(0,0,0,0.4);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    position: relative;
    transition: transform 0.1s;
  }
  .pit:hover {
    transform: scale(1.05);
    border-color: #faedcd;
  }
  .pit.playable {
    border-color: #52b788;
    box-shadow: inset 0 8px 12px rgba(0,0,0,0.9), 0 0 10px #52b788;
  }
  .pit-label {
    position: absolute;
    top: 2px;
    font-size: 9px;
    color: #d4a373;
    font-weight: bold;
  }
  .seeds-container {
    display: flex;
    flex-wrap: wrap;
    width: 42px;
    height: 42px;
    align-items: center;
    justify-content: center;
    gap: 2px;
    margin-top: 10px;
  }
  .seed-3d {
    width: 11px;
    height: 11px;
    background: radial-gradient(circle at 35% 35%, #ffb703, #b5651d 60%, #53330b);
    border-radius: 50%;
    box-shadow: 1px 2px 3px rgba(0,0,0,0.8), inset -1px -1px 2px rgba(0,0,0,0.5);
    display: inline-block;
  }
  #status-bar {
    font-size: 15px;
    margin: 15px 0;
    padding: 8px;
    background: #432818;
    border-radius: 8px;
    border: 1px solid #bb9457;
  }
  button.action-btn {
    background: #bc6c25;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
    cursor: pointer;
    margin: 5px;
  }
  button.action-btn:hover {
    background: #dda15e;
  }
</style>
</head>
<body>

  <div id="status-bar">Tap any glowing green pit (2+ seeds) to start sowing counter-clockwise!</div>

  <div id="board-container">
    <div style="font-size:12px; color:#dda15e; margin-bottom:5px;">AI COACH SIDE (Top)</div>
    <!-- AI Outer Row (15 down to 8) -->
    <div class="row" id="ai-outer"></div>
    <!-- AI Inner Row (7 down to 0) -->
    <div class="row" id="ai-inner"></div>

    <hr style="border-color: #8B4513; margin: 15px 0;">

    <!-- Learner Inner Row (0 up to 7) -->
    <div class="row" id="p-inner"></div>
    <!-- Learner Outer Row (15 down to 8) -->
    <div class="row" id="p-outer"></div>
    <div style="font-size:12px; color:#52b788; margin-top:5px;">YOUR SIDE (Bottom - Tap to Play)</div>
  </div>

  <div style="margin-top: 15px;">
    <button class="action-btn" onclick="resetGame()">Reset Board</button>
  </div>

<script>
  // Game State: 16 pits per player (0-7 inner, 8-15 outer)
  let p0 = [4,4,4,4,4,4,4,4, 0,0,0,0,0,0,0,0]; // Learner
  let p1 = [4,4,4,4,4,4,4,4, 0,0,0,0,0,0,0,0]; // AI Coach
  let isAnimating = false;

  // Web Audio API Sound Synthesizer for Falling Seed Clacks
  let audioCtx = null;
  function playSeedSound() {
    try {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      let osc = audioCtx.createOscillator();
      let gain = audioCtx.createGain();
      
      // Pitch drop simulates a small wooden seed dropping into a carved pit
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(400 + Math.random() * 150, audioCtx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime + 0.08);
      
      gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
      
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      
      osc.start();
      osc.stop(audioCtx.currentTime + 0.08);
    } catch(e) {
      // Audio context might be restricted before user interaction
    }
  }

  function renderBoard() {
    // Render AI Outer (15 -> 8)
    let htmlAIOuter = "";
    for (let i = 15; i >= 8; i--) {
      htmlAIOuter += createPitHTML(1, i, p1[i], false);
    }
    document.getElementById('ai-outer').innerHTML = htmlAIOuter;

    // Render AI Inner (7 -> 0)
    let htmlAIInner = "";
    for (let i = 7; i >= 0; i--) {
      htmlAIInner += createPitHTML(1, i, p1[i], false);
    }
    document.getElementById('ai-inner').innerHTML = htmlAIInner;

    // Render Learner Inner (0 -> 7)
    let htmlPInner = "";
    for (let i = 0; i <= 7; i++) {
      let playable = !isAnimating && p0[i] >= 2;
      htmlPInner += createPitHTML(0, i, p0[i], playable);
    }
    document.getElementById('p-inner').innerHTML = htmlPInner;

    // Render Learner Outer (15 -> 8)
    let htmlPOuter = "";
    for (let i = 15; i >= 8; i--) {
      let playable = !isAnimating && p0[i] >= 2;
      htmlPOuter += createPitHTML(0, i, p0[i], playable);
    }
    document.getElementById('p-outer').innerHTML = htmlPOuter;
  }

  function createPitHTML(player, index, count, playable) {
    let seedsHTML = "";
    // Limit displayed 3D seeds to 12 for visual neatness, show badge if more
    let displayCount = Math.min(count, 12);
    for (let s = 0; s < displayCount; s++) {
      seedsHTML += `<div class="seed-3d"></div>`;
    }
    if (count > 12) {
      seedsHTML += `<span style="font-size:9px; color:#ffb703; font-weight:bold;">+${count-12}</span>`;
    }

    let onclickAttr = (player === 0 && playable) ? `onclick="playTurn(${index})"` : "";
    let playableClass = playable ? "playable" : "";

    return `
      <div class="pit ${playableClass}" ${onclickAttr}>
        <span class="pit-label">P${index}</span>
        <div class="seeds-container">${seedsHTML}</div>
      </div>
    `;
  }

  // Sequential 3D Falling Seed Animation & Sowing Logic
  async function playTurn(startPit) {
    if (isAnimating) return;
    isAnimating = true;

    let seedsInHand = p0[startPit];
    p0[startPit] = 0;
    let curr = startPit;
    renderBoard();

    document.getElementById('status-bar').innerText = `Picking up ${seedsInHand} seeds from Pit ${startPit}...`;

    // Sowing loop with async delay so seeds fall one by one
    while (seedsInHand > 0) {
      await sleep(180); // Speed of each falling seed
      curr = (curr + 1) % 16;
      p0[curr] += 1;
      seedsInHand -= 1;
      
      playSeedSound();
      renderBoard();

      // Check if last seed landed
      if (seedsInHand === 0) {
        // Okutta Capture Check
        if (curr <= 7 && p0[curr] > 1) {
          let oppIn = 7 - curr;
          let oppOut = 8 + curr;
          if (p1[oppIn] > 0 && p1[oppOut] > 0) {
            let captured = p1[oppIn] + p1[oppOut];
            p1[oppIn] = 0;
            p1[oppOut] = 0;
            document.getElementById('status-bar').innerText = `✨ OKUTTA CAPTURE! Captured ${captured} seeds! Continuing relay...`;
            await sleep(600);
            seedsInHand = captured;
            curr = (startPit - 1) % 16;
            continue;
          }
        }
        // Relay Check
        if (p0[curr] >= 2) {
          seedsInHand = p0[curr];
          p0[curr] = 0;
          document.getElementById('status-bar').innerText = `🔄 RELAY! Picking up ${seedsInHand} seeds from Pit ${curr} to keep going!`;
          await sleep(400);
          continue;
        }
      }
    }

    document.getElementById('status-bar').innerText = "AI Coach is thinking...";
    await sleep(800);
    aiPlay();
    isAnimating = false;
    renderBoard();
  }

  function aiPlay() {
    let validAI = [];
    for (let i = 0; i < 16; i++) {
      if (p1[i] >= 2) validAI.push(i);
    }
    if (validAI.length === 0) {
      document.getElementById('status-bar').innerText = "🏆 You win! AI has no moves left.";
      return;
    }
    let aiPit = validAI[Math.floor(Math.random() * validAI.length)];
    let aiSeeds = p1[aiPit];
    p1[aiPit] = 0;
    let curr = aiPit;
    for (let s = 0; s < aiSeeds; s++) {
      curr = (curr + 1) % 16;
      p1[curr] += 1;
    }
    playSeedSound();
    document.getElementById('status-bar').innerText = `AI Coach played Pit ${aiPit}. Your turn!`;
  }

  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  function resetGame() {
    if (isAnimating) return;
    p0 = [4,4,4,4,4,4,4,4, 0,0,0,0,0,0,0,0];
    p1 = [4,4,4,4,4,4,4,4, 0,0,0,0,0,0,0,0];
    document.getElementById('status-bar').innerText = "Board reset. Tap any glowing green pit to play!";
    renderBoard();
  }

  // Initial render
  renderBoard();
</script>

</body>
</html>
"""

st.components.v1.html(omweso_html, height=520, scrolling=False)
