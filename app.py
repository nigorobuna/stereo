# app.py (一時的なテスト用コード)
import streamlit as st
import numpy as np
import matplotlib # matplotlib がインポートできるかだけ確認

st.set_page_config(page_title="デプロイテスト", layout="wide")
st.title("シンプルなデプロイテストアプリ 🚀")

st.write("このメッセージが表示されれば、基本的なStreamlitアプリの構造はデプロイ環境で動作しています。")
st.write(f"Streamlit バージョン: {st.__version__}")
st.write(f"NumPy バージョン: {np.__version__}")
st.write(f"Matplotlib バージョン: {matplotlib.__version__}") # インストールされたバージョンを確認

st.header("`projection_utils.py` のインポートテスト")

try:
    import projection_utils as pu
    st.success("`projection_utils.py` のインポートに成功しました！")

    # projection_utils.py の非常に簡単な関数をテスト的に呼び出してみる (もしあれば)
    # 例: pu.normalize があれば
    # test_vector = np.array([1.0, 2.0, 3.0])
    # normalized_vector = pu.normalize(test_vector)
    # st.write(f"`pu.normalize([1,2,3])` の呼び出し結果: {normalized_vector}")
    
    # projection_utils.py 内の定数を参照してみる (例: POLE_FAMILIES の最初の要素)
    if hasattr(pu, 'POLE_FAMILIES') and pu.POLE_FAMILIES:
         st.write(f"`pu.POLE_FAMILIES` の最初の要素のラベル: {pu.POLE_FAMILIES[0][1]}")
    else:
         st.write("`pu.POLE_FAMILIES` は見つからないか空です。")

except ImportError as e_import:
    st.error("`projection_utils.py` のインポートに失敗しました。")
    st.exception(e_import)
except Exception as e_general:
    st.error("`projection_utils.py` のインポート後、または使用中に予期せぬエラーが発生しました。")
    st.exception(e_general)

st.info("このテストページが正しく表示されたら、問題は元の `app.py` の複雑な部分にある可能性が高いです。その場合は、元のコードを少しずつ戻しながら原因箇所を特定します。")
st.warning("もしこのシンプルなテストページでも画面が真っ白になる、またはここでエラーが表示される場合は、Streamlit Community Cloudの「ランタイムログ」を再度ご確認ください。そこにサーバー側でのPythonエラーが記録されているはずです。")