"""
Arithmetic Coding Demo
Tugas Pertemuan 6 - Teori Informasi

"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from fractions import Fraction
from collections import Counter
import math


# ============================================================
# ALGORITMA ARITHMETIC CODING
# ============================================================

def validate_input(s: str):
    """Validasi: hanya huruf kecil dan spasi yang diperbolehkan."""
    if not s:
        return False, "Input tidak boleh kosong."
    for c in s:
        if not (c == ' ' or ('a' <= c <= 'z')):
            return False, f"Karakter '{c}' tidak valid. Hanya huruf kecil dan spasi yang diperbolehkan."
    return True, ""


def build_model(s: str):
    """Bangun tabel frekuensi, probabilitas, dan cumulative range.

    Output:
        n      : total karakter
        freq   : dict {char: count}
        chars  : list karakter terurut alfabetis (spasi paling depan)
        ranges : dict {char: (cum_low, cum_high)} dalam Fraction
    """
    n = len(s)
    freq = Counter(s)
    chars = sorted(freq.keys())  # spasi (ASCII 32) otomatis paling depan

    ranges = {}
    cum = 0
    for c in chars:
        lo = Fraction(cum, n)
        cum += freq[c]
        hi = Fraction(cum, n)
        ranges[c] = (lo, hi)

    return n, freq, chars, ranges


def encode(s: str, ranges):
    """Lakukan arithmetic encoding pakai Fraction (presisi eksak).

    Rumus per langkah:
        range  = high - low
        low'   = low + range * cum_low(c)
        high'  = low + range * cum_high(c)

    Output:
        low, high : interval akhir
        steps     : list (step_num, char, low, high) untuk visualisasi
    """
    low = Fraction(0)
    high = Fraction(1)
    steps = [(0, None, low, high)]  # state awal

    for i, c in enumerate(s, 1):
        rng = high - low
        cl, ch = ranges[c]
        new_high = low + rng * ch
        new_low = low + rng * cl
        low, high = new_low, new_high
        steps.append((i, c, low, high))

    return low, high, steps


def decode(value: Fraction, length: int, ranges):
    """Decode bilangan output kembali ke string asli (untuk verifikasi)."""
    chars = sorted(ranges.keys())
    result = []
    v = value
    for _ in range(length):
        for c in chars:
            cl, ch = ranges[c]
            if cl <= v < ch:
                result.append(c)
                # Skala ulang: pindahkan v ke [0,1) berdasarkan sub-interval terpilih
                v = (v - cl) / (ch - cl)
                break
    return ''.join(result)


def compute_entropy(freq, n):
    """Hitung entropi Shannon H(X) = sum p(x) * log2(1/p(x))."""
    return sum((freq[c] / n) * math.log2(n / freq[c]) for c in freq)


# ============================================================
# UI STREAMLIT
# ============================================================

st.set_page_config(
    page_title="Arithmetic Coding Demo",
    page_icon="",
    layout="wide",
)

st.title("Arithmetic Coding Demo")
st.caption("Tugas Pertemuan 6 — Teori Informasi")

with st.expander("ℹ️ Apa itu Arithmetic Coding?", expanded=False):
    st.markdown("""
    **Arithmetic coding** mengkodekan **seluruh string menjadi satu bilangan pecahan** di interval [0, 1).

    Berbeda dengan Huffman yang memberi kode bit terpisah ke tiap karakter, arithmetic coding 
    menyempitkan interval [0, 1) tiap kali membaca satu karakter. Karakter yang lebih sering 
    muncul mendapat sub-interval yang lebih besar, jadi interval menyempit lebih lambat untuk 
    karakter "umum" secara efektif memakai bit lebih sedikit untuk merepresentasikannya.

    **Kaitan dengan teori (slide minggu lalu):** lebar interval akhir = ∏ p(xᵢ).
    Jadi −log₂(lebar) = Σ −log₂(p(xᵢ)) = Σ h(xᵢ) ≈ **H(X) × N bits** persis batas teoretis Shannon.
    Inilah kenapa arithmetic coding bisa mencapai entropi tanpa loss, sesuatu yang Huffman tidak bisa.
    """)

# ----------- Input -----------
st.subheader("Input String")
default_input = "ada sebuah tulisan yang menjadi percobaan"
text = st.text_input(
    "Masukkan string (huruf kecil dan spasi saja):",
    value=default_input,
    help="Contoh dari soal tugas: 'ada sebuah tulisan yang menjadi percobaan'"
)

if not text:
    st.info("Masukkan string untuk memulai encoding.")
    st.stop()

valid, err = validate_input(text)
if not valid:
    st.error(f"❌ {err}")
    st.stop()

# ----------- Jalankan algoritma -----------
n, freq, chars, ranges = build_model(text)
low, high, steps = encode(text, ranges)
midpoint = (low + high) / 2

# ----------- Statistik singkat -----------
col1, col2, col3 = st.columns(3)
col1.metric("Total karakter (N)", n)
col2.metric("Karakter unik", len(chars))
col3.metric("Step encoding", len(steps) - 1)

# ----------- Tabel probabilitas -----------
st.subheader("Tabel Probabilitas & Cumulative Range")
st.caption("Tiap karakter menempati sub-interval [cum_low, cum_high) dengan lebar = P(c).")

prob_df = pd.DataFrame([
    {
        "Karakter": "(spasi)" if c == ' ' else c,
        "Frekuensi": freq[c],
        "P(c)": f"{freq[c]}/{n}",
        "P(c) ≈": f"{freq[c]/n:.4f}",
        "cum_low": str(ranges[c][0]),
        "cum_high": str(ranges[c][1]),
        "cum_low ≈": f"{float(ranges[c][0]):.4f}",
        "cum_high ≈": f"{float(ranges[c][1]):.4f}",
    }
    for c in chars
])
st.dataframe(prob_df, use_container_width=True, hide_index=True)

# ----------- Visualisasi penyempitan interval -----------
st.subheader("Visualisasi Penyempitan Interval")
st.caption("Interval menyempit secara eksponensial itulah kenapa kita harus pakai `Fraction`, bukan `float`.")

# Chart 1: lebar interval per step (skala log)
step_widths = [float(s[3] - s[2]) for s in steps]
step_nums = list(range(len(steps)))

fig_width = go.Figure()
fig_width.add_trace(go.Scatter(
    x=step_nums,
    y=step_widths,
    mode='lines+markers',
    line=dict(color='#6B5B95', width=2),
    marker=dict(size=6, color='#6B5B95'),
    hovertemplate='Step %{x}<br>Lebar: %{y:.3e}<extra></extra>'
))
fig_width.update_layout(
    title="Lebar interval per step (skala log)",
    xaxis_title="Step",
    yaxis_title="Lebar interval",
    yaxis_type="log",
    height=350,
    template="plotly_white",
    margin=dict(l=20, r=20, t=50, b=20),
)
st.plotly_chart(fig_width, use_container_width=True)

# Chart 2: detail per step dengan slider
if len(steps) > 2:
    st.markdown("**Detail tiap step** — geser slider untuk melihat penyempitan interval per langkah:")
    selected_step = st.slider("Step", 1, len(steps) - 1, min(3, len(steps) - 1))

    prev_low, prev_high = steps[selected_step - 1][2], steps[selected_step - 1][3]
    curr_step, curr_char, curr_low, curr_high = steps[selected_step]
    prev_range = prev_high - prev_low

    # Bangun sub-interval untuk interval sebelumnya, dibagi per karakter
    fig_div = go.Figure()
    for c in chars:
        cl, ch = ranges[c]
        sub_lo = prev_low + prev_range * cl
        sub_hi = prev_low + prev_range * ch
        is_chosen = (c == curr_char)
        label = "_" if c == ' ' else c

        fig_div.add_trace(go.Bar(
            x=[float(sub_hi - sub_lo)],
            y=['Sub-interval'],
            orientation='h',
            marker=dict(
                color='#FF6B6B' if is_chosen else '#D0D0D0',
                line=dict(color='#333', width=0.5),
            ),
            text=label,
            textposition='inside',
            textfont=dict(color='white' if is_chosen else '#333', size=12),
            hovertemplate=f"'{label}'<br>[{float(sub_lo):.6f}, {float(sub_hi):.6f})<extra></extra>",
            showlegend=False,
        ))

    char_label = "(spasi)" if curr_char == ' ' else f"'{curr_char}'"
    fig_div.update_layout(
        barmode='stack',
        title=f"Step {curr_step}: baca {char_label} → pilih sub-interval merah",
        height=180,
        xaxis=dict(
            title=f"Interval sebelumnya: [{float(prev_low):.10f}, {float(prev_high):.10f})",
            showticklabels=False,
        ),
        yaxis=dict(showticklabels=False),
        template="plotly_white",
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=40),
    )
    st.plotly_chart(fig_div, use_container_width=True)

    # Detail numerik step terpilih
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Sebelum step ini:**")
        st.code(
            f"low  = {float(prev_low):.15f}\n"
            f"high = {float(prev_high):.15f}\n"
            f"lebar = {float(prev_range):.4e}",
            language=None,
        )
    with col2:
        st.markdown(f"**Sesudah baca {char_label}:**")
        st.code(
            f"low  = {float(curr_low):.15f}\n"
            f"high = {float(curr_high):.15f}\n"
            f"lebar = {float(curr_high - curr_low):.4e}",
            language=None,
        )

# ----------- Tabel lengkap step encoding -----------
with st.expander(f"Tabel Lengkap {len(steps)-1} Step Encoding"):
    steps_df = pd.DataFrame([
        {
            "Step": s[0],
            "Karakter": "(init)" if s[1] is None else ("(spasi)" if s[1] == ' ' else s[1]),
            "low ≈": f"{float(s[2]):.15f}",
            "high ≈": f"{float(s[3]):.15f}",
            "lebar ≈": f"{float(s[3] - s[2]):.4e}",
        }
        for s in steps
    ])
    st.dataframe(steps_df, use_container_width=True, hide_index=True)

# ----------- Hasil akhir -----------
st.subheader("Hasil Akhir Arithmetic Coding")

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("**Interval akhir [low, high):**")
    st.code(
        f"low  = {float(low):.20f}\n"
        f"high = {float(high):.20f}\n"
        f"lebar = {float(high - low):.4e}",
        language=None,
    )
with col2:
    st.markdown("**Bilangan output (titik tengah interval):**")
    st.code(f"{float(midpoint):.20f}", language=None)
    st.caption("Bilangan ini merepresentasikan seluruh string yang di-encode.")

# ----------- Analisis entropi -----------
st.subheader("Analisis Entropi (Kaitan dengan Teori Shannon)")

entropy = compute_entropy(freq, n)
total_bits_theory = entropy * n
total_bits_actual = -math.log2(float(high - low)) if float(high - low) > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("H(X) per karakter", f"{entropy:.4f} bits")
col2.metric("H × N (batas Shannon)", f"{total_bits_theory:.4f} bits")
col3.metric("−log₂(lebar) aktual", f"{total_bits_actual:.4f} bits")

if abs(total_bits_theory - total_bits_actual) < 0.01:
    st.success(
        "✅ **Hasil aktual = batas teoretis Shannon (H × N).** "
        "Inilah keunggulan arithmetic coding: mencapai entropi tanpa loss — "
        "sesuatu yang Huffman tidak bisa karena harus pakai panjang kode bilangan bulat."
    )

# ----------- Verifikasi decoding -----------
st.subheader("Verifikasi: Decoding Output Kembali ke Input")
st.caption("Untuk membuktikan encoding-nya reversible, kita decode bilangan output kembali ke string aslinya.")

decoded = decode(midpoint, n, ranges)
if decoded == text:
    st.success("✅ Decoded berhasil dan **sama persis** dengan input asli:")
    st.code(decoded, language=None)
else:
    st.error("❌ Decoded tidak sama:")
    st.code(decoded, language=None)