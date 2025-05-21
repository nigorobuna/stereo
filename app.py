# app.py (ステップ1の状態)
import streamlit as st
import numpy as np
import matplotlib # これは元のテスト用app.pyにあったもの
import matplotlib.pyplot as plt # ← 元のapp.pyに合わせて追加
import projection_utils as pu

# --- 元のapp.pyからコピーしてきた描画関数の定義 ---
def plot_dynamic_stereographic_projection(center_h, center_k, center_l):
    # fig, ax = plt.subplots(...) # この行から始まるはず
    # ... (元の関数の処理がずっと続く) ...
    # return fig
# --- 関数の定義ここまで ---

st.set_page_config(page_title="デプロイテスト", layout="wide")
st.title("シンプルなデプロイテストアプリ 🚀")
# ... (前回動いたインポートテストの表示などはそのまま残しておいてOK) ...

# まだ plot_dynamic_stereographic_projection は呼び出さない
st.info("ステップ1：描画関数の定義を追加しました。まだ呼び出していません。")

# app.py (ステップ2の状態。ステップ1のコードに続けて...)

# ... (st.info(...) の後など) ...
st.header("固定値でのプロットテスト")
try:
    # 固定値で描画関数を呼び出す
    fig_test_plot = plot_dynamic_stereographic_projection(0, 0, 1) # 例えば[001]でテスト
    st.pyplot(fig_test_plot)
    st.success("[001]中心のプロットテスト（固定値）成功！")
except Exception as e_plot:
    st.error("固定値でのプロット中にエラーが発生しました。")
    st.exception(e_plot) # エラーの詳細を表示