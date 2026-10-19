
import streamlit as st
import sqlite3
import random
import time
import html
from pathlib import Path

# =========================
# CẤU HÌNH TRÒ CHƠI
# =========================
st.set_page_config(
    
# =========================
# NHẠC NỀN UFO HACK NÃO
# =========================
import streamlit.components.v1 as components

st.markdown("""
<style>
.music-panel {
    background: linear-gradient(135deg, #171b3b, #302050);
    border: 1px solid #6b70d9;
    border-radius: 16px;
    padding: 12px 16px;
    margin: 12px 0;
    color: white;
    text-align: center;
}
.music-panel p {
    margin: 4px 0;
    color: #c8d8ff;
}
</style>
<div class="music-panel">
    <div style="font-size:22px">🎵 UFO SPACE RADIO</div>
    <p>Nhạc nền vũ trụ • Bật nhạc để bắt đầu chuyến phiêu lưu!</p>
</div>
""", unsafe_allow_html=True)

components.html("""
<div style="
    background:#11152f;
    border:1px solid #555bb0;
    border-radius:14px;
    padding:12px;
    color:white;
    font-family:Arial,sans-serif;
    text-align:center;
">
    <button id="play" style="
        background:linear-gradient(90deg,#5145cd,#168fa8);
        color:white;border:0;border-radius:10px;
        padding:12px 22px;font-weight:bold;
        cursor:pointer;font-size:15px;
    ">▶ BẬT NHẠC VŨ TRỤ</button>

    <p style="margin:12px 0 5px">🔊 Âm lượng</p>
    <input id="vol" type="range" min="0" max="100"
           value="25" style="width:85%;cursor:pointer">
    <p id="status" style="color:#a9e9ff;font-size:12px">
        Nhấn nút để bật nhạc
    </p>
</div>

<script>
const btn = document.getElementById("play");
const vol = document.getElementById("vol");
const status = document.getElementById("status");

let ctx = null;
let master = null;
let oscillators = [];
let playing = false;

function startMusic() {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain();
    master.gain.value = Number(vol.value) / 100 * 0.12;
    master.connect(ctx.destination);

    // Âm thanh tổng hợp nhẹ nhàng kiểu không gian
    const notes = [110, 164.81, 220, 146.83];

    notes.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        const filter = ctx.createBiquadFilter();

        osc.type = i % 2 === 0 ? "sine" : "triangle";
        osc.frequency.value = freq;
        filter.type = "lowpass";
        filter.frequency.value = 450;

        gain.gain.value = i === 0 ? 0.5 : 0.12;
        osc.connect(filter);
        filter.connect(gain);
        gain.connect(master);
        osc.start();

        oscillators.push(osc);
    });

    // Âm thanh nền biến đổi chậm, không cần tải file nhạc
    const lfo = ctx.createOscillator();
    const lfoGain = ctx.createGain();
    lfo.frequency.value = 0.08;
    lfoGain.gain.value = 25;
    lfo.connect(lfoGain);
    lfoGain.connect(oscillators[0].frequency);
    lfo.start();
    oscillators.push(lfo);
}

btn.onclick = async () => {
    try {
        if (!playing) {
            if (!ctx) startMusic();
            await ctx.resume();
            playing = true;
            btn.textContent = "⏸ TẮT NHẠC";
            status.textContent = "Đang phát âm thanh không gian";
        } else {
            await ctx.suspend();
            playing = false;
            btn.textContent = "▶ BẬT NHẠC VŨ TRỤ";
            status.textContent = "Nhạc đang tạm dừng";
        }
    } catch (e) {
        status.textContent = "Trình duyệt chưa cho phép phát âm thanh";
    }
};

vol.oninput = () => {
    if (master && ctx) {
        master.gain.setTargetAtTime(
            Number(vol.value) / 100 * 0.12,
            ctx.currentTime,
            0.05
        );
    }
};
</script>
""", height=190)

    page_title="UFO HACK NÃO",
    page_icon="👽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_FILE = Path(__file__).with_name("ufo_scores.db")

# =========================
# CÂU ĐỐ
# =========================
QUESTIONS = [
    {
        "q": "Bạn vượt qua người đứng thứ hai trong cuộc đua. Bạn đứng thứ mấy?",
        "a": ["Thứ nhất", "Thứ hai", "Thứ ba", "Cuối cùng"],
        "correct": 1,
        "explain": "Bạn chiếm vị trí của người thứ hai, nên bạn đứng thứ hai!"
    },
    {
        "q": "Có 5 máy làm ra 5 sản phẩm trong 5 phút. 100 máy làm ra 100 sản phẩm trong bao lâu?",
        "a": ["100 phút", "20 phút", "5 phút", "1 phút"],
        "correct": 2,
        "explain": "Mỗi máy làm một sản phẩm trong 5 phút. 100 máy làm đồng thời nên vẫn mất 5 phút."
    },
    {
        "q": "Một năm có bao nhiêu tháng có 28 ngày?",
        "a": ["1 tháng", "2 tháng", "6 tháng", "12 tháng"],
        "correct": 3,
        "explain": "Tất cả 12 tháng đều có ít nhất 28 ngày."
    },
    {
        "q": "Số tiếp theo của dãy 2, 6, 12, 20, 30, ... là gì?",
        "a": ["36", "40", "42", "44"],
        "correct": 2,
        "explain": "Dãy lần lượt là 1×2, 2×3, 3×4, 4×5, 5×6. Tiếp theo là 6×7 = 42."
    },
    {
        "q": "Bố của Lan có 5 người con: Na, Ne, Ni, No. Người con thứ năm tên gì?",
        "a": ["Nu", "Lan", "Na", "Không xác định"],
        "correct": 1,
        "explain": "Đề bài đã nói bố của Lan, vậy người con thứ năm là Lan."
    },
    {
        "q": "Bạn có 3 công tắc bên ngoài phòng kín. Chỉ một công tắc bật bóng đèn trong phòng. Bạn được vào phòng một lần. Điều gì giúp phân biệt công tắc đúng?",
        "a": [
            "Chỉ nhìn bóng đèn",
            "Dùng nhiệt của bóng đèn",
            "Đoán ngẫu nhiên",
            "Không thể làm được"
        ],
        "correct": 1,
        "explain": "Bật công tắc 1 một lúc rồi tắt, bật công tắc 2 và vào phòng. Đèn sáng là công tắc 2; đèn tắt nhưng bóng ấm là công tắc 1; đèn tắt và nguội là công tắc 3."
    },
    {
        "q": "Một con ốc sên leo cột cao 10 m. Ban ngày leo 3 m, ban đêm tụt 2 m. Nó cần bao nhiêu ngày để lên đỉnh?",
        "a": ["8 ngày", "9 ngày", "10 ngày", "7 ngày"],
        "correct": 1,
        "explain": "Sau 8 đêm, ốc sên ở độ cao 8 m. Ngày thứ 9 leo thêm 3 m và chạm đỉnh."
    },
    {
        "q": "Nếu 2 con mèo bắt 2 con chuột trong 2 phút, 10 con mèo bắt 10 con chuột trong bao lâu?",
        "a": ["10 phút", "2 phút", "5 phút", "20 phút"],
        "correct": 1,
        "explain": "Mỗi con mèo bắt một con chuột trong 2 phút, nên 10 con làm đồng thời cũng mất 2 phút."
    },
    {
        "q": "Một chiếc đồng hồ điểm 6 tiếng trong 5 giây. Nó điểm 12 tiếng trong bao lâu?",
        "a": ["10 giây", "11 giây", "12 giây", "15 giây"],
        "correct": 1,
        "explain": "6 tiếng điểm có 5 khoảng thời gian. 12 tiếng có 11 khoảng, nên mất 11 giây."
    },
    {
        "q": "Một số có hai chữ số. Tổng hai chữ số bằng 9. Đổi vị trí hai chữ số thì số mới lớn hơn số cũ 27. Số ban đầu là?",
        "a": ["36", "45", "27", "54"],
        "correct": 0,
        "explain": "36 có tổng 3 + 6 = 9. Đảo thành 63, lớn hơn 36 đúng 27."
    },
    {
        "q": "Bạn có 10 viên kẹo, cho đi 3 viên. Bạn còn bao nhiêu viên?",
        "a": ["3", "7", "10", "13"],
        "correct": 1,
        "explain": "10 - 3 = 7 viên."
    },
    {
        "q": "Điền số tiếp theo: 1, 1, 2, 3, 5, 8, ...",
        "a": ["11", "12", "13", "15"],
        "correct": 2,
        "explain": "Mỗi số bằng tổng hai số đứng trước: 5 + 8 = 13."
    },
    {
        "q": "Một căn phòng có 4 góc. Mỗi góc có một con mèo. Mỗi con mèo nhìn thấy 3 con mèo. Có tất cả bao nhiêu con?",
        "a": ["4", "8", "12", "16"],
        "correct": 0,
        "explain": "Có 4 con mèo, mỗi con nhìn thấy ba con còn lại."
    },
    {
        "q": "Nếu hôm kia là thứ Hai, ngày kia là thứ mấy?",
        "a": ["Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ nhật"],
        "correct": 1,
        "explain": "Hôm kia thứ Hai, hôm qua thứ Ba, hôm nay thứ Tư, ngày mai thứ Năm, ngày kia thứ Sáu."
    },
    {
        "q": "Số nào khác biệt: 4, 9, 16, 25, 36, 48, 64?",
        "a": ["16", "36", "48", "64"],
        "correct": 2,
        "explain": "Các số còn lại đều là số chính phương. 48 không phải số chính phương."
    },
    {
        "q": "Bạn có một que diêm, vào phòng tối có nến, đèn dầu và bếp. Bạn thắp gì trước?",
        "a": ["Nến", "Đèn dầu", "Bếp", "Que diêm"],
        "correct": 3,
        "explain": "Bạn phải thắp que diêm trước đã!"
    },
    {
        "q": "Một chiếc áo giá 200.000 đồng giảm 25%. Giá sau giảm là bao nhiêu?",
        "a": ["150.000 đồng", "175.000 đồng", "125.000 đồng", "50.000 đồng"],
        "correct": 0,
        "explain": "200.000 × 75% = 150.000 đồng."
    },
    {
        "q": "Có 3 hộp ghi Nhãn Táo, Nhãn Cam và Nhãn Táo-Cam. Cả 3 nhãn đều sai. Lấy một quả từ hộp nào để xác định lại cả ba hộp?",
        "a": [
            "Hộp ghi Táo",
            "Hộp ghi Cam",
            "Hộp ghi Táo-Cam",
            "Bất kỳ hộp nào"
        ],
        "correct": 2,
        "explain": "Hộp ghi Táo-Cam chắc chắn không phải hộp trộn. Lấy một quả từ đó để biết nó là hộp táo hay cam, rồi suy ra hai hộp còn lại."
    },
    {
        "q": "Nếu 3 người xây 3 bức tường trong 3 ngày, 6 người xây 6 bức tường trong bao lâu, với năng suất như nhau?",
        "a": ["1 ngày", "2 ngày", "3 ngày", "6 ngày"],
        "correct": 2,
        "explain": "Mỗi người xây một bức tường trong 3 ngày, nên 6 người xây 6 bức tường trong 3 ngày."
    },
    {
        "q": "Một chiếc thuyền có thang treo bên mạn. Nước dâng lên 1 m. Thuyền nổi lên theo nước. Thang có ngập sâu hơn không?",
        "a": ["Có, 1 m", "Có, 0,5 m", "Không", "Không thể biết"],
        "correct": 2,
        "explain": "Thuyền nổi lên cùng mặt nước nên vị trí tương đối giữa thuyền và mặt nước không đổi."
    }
]

# =========================
# CƠ SỞ DỮ LIỆU BẢNG ĐIỂM
# =========================
def init_db():
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player TEXT NOT NULL,
                score INTEGER NOT NULL,
                correct INTEGER NOT NULL,
                total INTEGER NOT NULL,
                created REAL NOT NULL
            )
        """)

def save_score(player, score, correct, total):
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        conn.execute(
            "INSERT INTO scores(player, score, correct, total, created) VALUES (?, ?, ?, ?, ?)",
            (player, score, correct, total, time.time())
        )

def get_scores():
    with sqlite3.connect(DB_FILE, timeout=10) as conn:
        return conn.execute("""
            SELECT player, score, correct, total
            FROM scores
            ORDER BY score DESC, correct DESC, created ASC
            LIMIT 100
        """).fetchall()

init_db()

# =========================
# GIAO DIỆN
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;800&family=Nunito:wght@400;600;700;800&display=swap');

:root {
    --cyan: #4deaff;
    --purple: #b48cff;
    --pink: #ff78c9;
    --panel: rgba(19, 24, 55, .88);
}

.stApp {
    background:
        radial-gradient(ellipse at 10% 10%, #25285c 0%, transparent 35%),
        radial-gradient(ellipse at 90% 35%, #302050 0%, transparent 30%),
        linear-gradient(145deg, #080b1b, #11132d 60%, #090c20);
    color: #f7f7ff;
    font-family: 'Nunito', sans-serif;
}

.block-container {
    max-width: 1050px;
    padding: 1.2rem 1rem 3rem;
}

h1, h2, h3 {
    color: #ffffff !important;
    font-family: 'Orbitron', sans-serif !important;
}

.ufo-title {
    text-align: center;
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(2rem, 6vw, 4rem);
    font-weight: 800;
    line-height: 1.2;
    color: #8cf4ff;
    text-shadow: 0 0 12px #24cfff, 0 0 35px #795dff;
    animation: glow 3s ease-in-out infinite alternate;
}
.subtitle {
    text-align: center;
    color: #d5cfff;
    font-size: 1.05rem;
    margin: .7rem 0 1.5rem;
}
@keyframes glow {
    from { text-shadow: 0 0 10px #24cfff; }
    to { text-shadow: 0 0 18px #24cfff, 0 0 38px #aa70ff; }
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-7px); }
}
.ufo {
    text-align: center;
    font-size: 4rem;
    animation: float 3s ease-in-out infinite;
    filter: drop-shadow(0 0 16px #42eaff);
}
.panel {
    background: var(--panel);
    border: 1px solid rgba(120, 195, 255, .30);
    border-radius: 22px;
    padding: clamp(16px, 3vw, 28px);
    box-shadow: 0 8px 35px rgba(0,0,0,.20);
    margin: 12px 0;
}
.question {
    font-size: clamp(1.15rem, 3vw, 1.55rem);
    font-weight: 800;
    line-height: 1.6;
    color: #fff;
}
.small-note {
    color: #bfc9ed;
    font-size: .9rem;
}
div.stButton > button {
    min-height: 48px;
    border-radius: 13px;
    border: 1px solid #5fbcff;
    background: linear-gradient(110deg, #29285f, #382c70);
    color: white;
    font-weight: 800;
    transition: transform .18s ease, box-shadow .18s ease;
    width: 100%;
}
div.stButton > button:hover {
    border-color: #83f5ff;
    color: white;
    box-shadow: 0 0 17px #36d8ff66;
    transform: translateY(-2px);
}
div.stButton > button:active {
    transform: scale(.98);
}
.stTextInput input {
    border-radius: 12px;
}
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #38e9ff, #c18aff, #ff79c9);
}
div[data-testid="stMetric"] {
    background: rgba(42, 43, 91, .7);
    border: 1px solid #4d5b98;
    padding: 13px;
    border-radius: 15px;
}
hr { border-color: #393e70; }
footer { visibility: hidden; }
@media(max-width: 600px) {
    .block-container { padding: .6rem .65rem 2rem; }
    .ufo { font-size: 3rem; }
    .panel { border-radius: 16px; padding: 15px; }
    div.stButton > button { min-height: 48px; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="ufo">🛸</div>', unsafe_allow_html=True)
st.markdown('<div class="ufo-title">UFO HACK NÃO</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">👽 Giải mã bí ẩn • Đánh thức trí não • Chinh phục vũ trụ</div>',
    unsafe_allow_html=True
)

# =========================
# TRẠNG THÁI NGƯỜI CHƠI
# =========================
defaults = {
    "screen": "home",
    "player": "",
    "questions": [],
    "index": 0,
    "score": 0,
    "correct": 0,
    "answered": False,
    "selected": None,
    "feedback": "",
    "finished": False,
    "saved": False,
    "round_id": 0
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================
# TRANG CHỦ
# =========================
if st.session_state.screen == "home":
    st.markdown("""
    <div class="panel">
      <div class="question">🌌 Phi hành gia, bạn đã sẵn sàng?</div>
      <p>Vượt qua những câu đố đánh lừa tư duy để trở thành bộ não thiên hà.</p>
      <p>✨ 10 câu hỏi mỗi lượt &nbsp; • &nbsp; 🏆 Tích lũy điểm &nbsp; • &nbsp; 🚀 4 lựa chọn mỗi câu</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("start_form"):
        name = st.text_input(
            "👾 Tên phi hành gia",
            max_chars=20,
            placeholder="Ví dụ: UFO_Pro"
        )
        difficulty = st.selectbox(
            "🎮 Chế độ thử thách",
            ["Du hành", "Thử thách", "Siêu hack não"],
            help="Chế độ thay đổi số điểm nhận được cho mỗi câu đúng."
        )
        submitted = st.form_submit_button(
            "🚀 KHỞI ĐỘNG UFO",
            use_container_width=True
        )

    if submitted:
        clean_name = " ".join(name.strip().split())
        if not clean_name:
            st.warning("Bạn hãy nhập tên phi hành gia trước nhé!")
        else:
            st.session_state.player = clean_name
            st.session_state.difficulty = difficulty
            st.session_state.questions = random.sample(QUESTIONS, 10)
            st.session_state.index = 0
            st.session_state.score = 0
            st.session_state.correct = 0
            st.session_state.answered = False
            st.session_state.selected = None
            st.session_state.feedback = ""
            st.session_state.finished = False
            st.session_state.saved = False
            st.session_state.round_id += 1
            st.session_state.screen = "game"
            st.rerun()

    st.markdown("### 🏆 Bảng xếp hạng phi hành gia")
    scores = get_scores()
    if scores:
        for rank, row in enumerate(scores[:10], start=1):
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}
            st.markdown(
                f"**{medals.get(rank, str(rank) + '.')} {html.escape(row[0])}**"
                f" — {row[1]} điểm · đúng {row[2]}/{row[3]}"
            )
    else:
        st.info("Chưa có phi hành gia nào. Bạn hãy là người đầu tiên!")

    st.caption("Bảng điểm lưu trên máy chủ đang chạy ứng dụng. Nếu máy chủ khởi động lại hoặc đổi phiên bản, dữ liệu cục bộ có thể bị mất.")

# =========================
# MÀN HÌNH CÂU ĐỐ
# =========================
elif st.session_state.screen == "game":
    questions = st.session_state.questions
    idx = st.session_state.index
    q = questions[idx]
    total = len(questions)

    st.progress((idx + (1 if st.session_state.answered else 0)) / total)
    left, right = st.columns(2)
    left.metric("🧠 Câu hỏi", f"{idx + 1}/{total}")
    right.metric("⭐ Điểm số", st.session_state.score)

    st.markdown(
        f'<div class="panel"><div class="small-note">'
        f'PHI HÀNH GIA: {html.escape(st.session_state.player)}'
        f'</div><div class="question">{html.escape(q["q"])}</div></div>',
        unsafe_allow_html=True
    )

    if not st.session_state.answered:
        for start in range(0, 4, 2):
            cols = st.columns(2)
            for offset, col in enumerate(cols):
                choice = start + offset
                with col:
                    if st.button(
                        f"{chr(65 + choice)}. {q['a'][choice]}",
                        key=f"answer_{st.session_state.round_id}_{idx}_{choice}",
                        use_container_width=True
                    ):
                        st.session_state.selected = choice
                        st.session_state.answered = True
                        if choice == q["correct"]:
                            st.session_state.correct += 1
                            multiplier = {
                                "Du hành": 10,
                                "Thử thách": 20,
                                "Siêu hack não": 30
                            }.get(st.session_state.get("difficulty", "Du hành"), 10)
                            st.session_state.score += multiplier
                            st.session_state.feedback = "correct"
                        else:
                            st.session_state.feedback = "wrong"
                        st.rerun()
    else:
        if st.session_state.feedback == "correct":
            st.success("🎉 Chính xác! Bạn nhận được điểm.")
        else:
            correct_answer = q["a"][q["correct"]]
            st.error(f"🛸 Chưa chính xác! Đáp án đúng: {correct_answer}")

        st.info("💡 Giải mã: " + q["explain"])

        if idx + 1 < total:
            if st.button("➡️ CÂU TIẾP THEO", use_container_width=True):
                st.session_state.index += 1
                st.session_state.answered = False
                st.session_state.selected = None
                st.session_state.feedback = ""
                st.rerun()
        else:
            if st.button("🏆 XEM KẾT QUẢ", use_container_width=True):
                st.session_state.screen = "result"
                st.rerun()

    st.markdown("---")
    if st.button("🏠 Thoát về trang chủ", use_container_width=True):
        st.session_state.screen = "home"
        st.rerun()

# =========================
# KẾT QUẢ
# =========================
elif st.session_state.screen == "result":
    if not st.session_state.saved:
        save_score(
            st.session_state.player,
            st.session_state.score,
            st.session_state.correct,
            len(st.session_state.questions)
        )
        st.session_state.saved = True

    correct = st.session_state.correct
    total = len(st.session_state.questions)
    percent = round(correct / total * 100)

    st.balloons()
    st.markdown(
        '<div class="panel"><div class="question">'
        '🌠 NHIỆM VỤ HOÀN TẤT!</div></div>',
        unsafe_allow_html=True
    )
    st.markdown(f"### Xin chúc mừng, {html.escape(st.session_state.player)}!")
    a, b, c = st.columns(3)
    a.metric("⭐ Tổng điểm", st.session_state.score)
    b.metric("✅ Trả lời đúng", f"{correct}/{total}")
    c.metric("🧠 Chính xác", f"{percent}%")

    if percent == 100:
        st.success("👑 Huyền thoại trí não! Bạn đã giải mã toàn bộ thử thách.")
    elif percent >= 70:
        st.success("🚀 Xuất sắc! Bạn là phi hành gia rất thông minh.")
    elif percent >= 40:
        st.info("🛸 Khá lắm! Thử thêm một lượt để luyện tư duy.")
    else:
        st.warning("🌱 Đừng bỏ cuộc! Mỗi câu đố là một cơ hội học thêm.")

    st.markdown("### 🏆 Bảng xếp hạng")
    for rank, row in enumerate(get_scores()[:10], start=1):
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        st.write(
            f"{medals.get(rank, str(rank) + '.')}"
            f" **{html.escape(row[0])}** — {row[1]} điểm"
            f" · đúng {row[2]}/{row[3]}"
        )

    if st.button("🔄 CHƠI LẠI", use_container_width=True):
        st.session_state.screen = "home"
        st.rerun()

    if st.button("🏠 VỀ TRANG CHỦ", use_container_width=True):
        st.session_state.screen = "home"
        st.rerun()
