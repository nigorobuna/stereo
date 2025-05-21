# projection_utils.py

import numpy as np
import itertools
import functools

# --- Unicodeオーバーラインを使ったラベルフォーマット関数 ---
def format_hkl_label_unicode(h, k, l, with_brackets=True):
    """ミラー指数をUnicodeオーバーラインでフォーマットする"""
    s_h = f"{abs(h)}\u0305" if h < 0 else str(h)
    s_k = f"{abs(k)}\u0305" if k < 0 else str(k)
    s_l = f"{abs(l)}\u0305" if l < 0 else str(l)
    if with_brackets:
        return f"[{s_h}{s_k}{s_l}]"
    return f"{s_h}{s_k}{s_l}"

# --- ベクトル正規化 ---
def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0:
        return v # ゼロベクトルはそのまま返す
    return v / norm

# --- 新しい基底ベクトル（回転）を計算 ---
def get_rotation_basis_vectors(h, k, l):
    """
    指定された[hkl]方向が新しいZ軸(z_new_axis)となるような
    正規直交基底 (x_new_axis, y_new_axis, z_new_axis) を計算する。
    """
    # 入力h,k,lが(0,0,0)でないことは呼び出し元で保証する前提
    z_new_axis = normalize(np.array([h, k, l], dtype=float))
    
    # 元のZ軸 (0,0,1)
    original_z_axis = np.array([0., 0., 1.])
    
    # z_new_axis が original_z_axis と平行かどうかチェック
    if np.linalg.norm(np.cross(original_z_axis, z_new_axis)) < 1e-6: # 平行の場合
        # z_new_axisが(0,0,+-1)なので、x_new_axisは(1,0,0)とできる
        x_new_axis = normalize(np.array([1., 0., 0.]))
    else: # 平行でない場合
        # x_new_axis は original_z_axis と z_new_axis の外積から生成
        x_new_axis = normalize(np.cross(original_z_axis, z_new_axis))
    
    # y_new_axis は z_new_axis と x_new_axis の外積から生成 (右手系)
    y_new_axis = normalize(np.cross(z_new_axis, x_new_axis))
    
    # x_new_axis を y_new_axis と z_new_axis から再計算して厳密に直交させる (念のため)
    x_new_axis = normalize(np.cross(y_new_axis, z_new_axis))

    return x_new_axis, y_new_axis, z_new_axis

# --- 指定された方向を新しい基底で表現し、ステレオ投影 ---
def project_pole_in_new_basis(original_hkl, x_new_axis, y_new_axis, z_new_axis):
    """
    元の結晶座標系での方向 original_hkl を、新しい基底で表現し、
    その新しいZ軸の南極からステレオ投影する。
    """
    pole_original_vec = normalize(np.array(original_hkl, dtype=float))

    # 元の方向ベクトルを新しい基底で表現 (内積を取る)
    x_in_new_basis = np.dot(pole_original_vec, x_new_axis)
    y_in_new_basis = np.dot(pole_original_vec, y_new_axis)
    z_in_new_basis = np.dot(pole_original_vec, z_new_axis)

    # ステレオ投影 (新しいZ軸の南極 (0,0,-1)_new からXY平面へ)
    # z_in_new_basis が -1 に近い場合は無限遠点になるのでプロットしない
    if abs(1 + z_in_new_basis) < 1e-9:
        return None, None 
    
    proj_X = x_in_new_basis / (1 + z_in_new_basis)
    proj_Y = y_in_new_basis / (1 + z_in_new_basis)
    
    return proj_X, proj_Y

# --- 表示する結晶方位ファミリーの定義 ---
# ( (h,k,l)_representative, "family_label_prefix", "marker", "color", size_factor )
POLE_FAMILIES = [
    ((1,0,0), "<100>", "s", "blue", 1.2),
    ((1,1,0), "<110>", "D", "red", 1.1),
    ((1,1,1), "<111>", "^", "forestgreen", 1.0), # 色をforestgreenに変更
    ((2,1,0), "<210>", "o", "purple", 0.9),
    ((2,1,1), "<211>", "o", "deepskyblue", 0.8), # 色をdeepskyblueに変更
    ((3,1,0), "<310>", "o", "magenta", 0.8),
    ((3,2,1), "<321>", "o", "saddlebrown", 0.8), # <321> を追加
    # ((3,3,1), "<331>", "p", "black", 0.9), # 例として五角形(pentagon)マーカー
]

# --- 表示する結晶方位のリスト (立方晶の対称性を考慮して生成) ---
@functools.lru_cache(maxsize=None) # 計算結果をキャッシュ
def get_poles_to_display(families_indices_tuple):
    """
    指定されたミラー指数のファミリーから、対称的に等価な方向をリストアップする。
    families_indices_tuple: ( (h,k,l), "label_prefix", "marker", "color", size_factor ) のタプル
    """
    families_indices = list(families_indices_tuple) # タプルをリストに戻して処理
    poles = []
    seen_hkl_tuples_for_family_labeling = {} # ラベル付けのための重複管理

    for representative_indices, family_label_prefix, marker, color, size_f in families_indices:
        h_rep, k_rep, l_rep = representative_indices
        
        # abs値の順列を生成 (例: (2,1,0) -> (2,1,0), (2,0,1), (1,2,0), (0,2,1), (1,0,2), (0,1,2) の絶対値)
        abs_values_of_rep = sorted([abs(h_rep), abs(k_rep), abs(l_rep)])
        
        # 生成するべき順列は、元の指数の非ゼロ要素の数と値に依存
        # ここでは簡易的に、代表指数の絶対値の全ての順列を試す
        unique_abs_permutations = set(itertools.permutations(abs_values_of_rep))

        for p_abs in unique_abs_permutations:
            # 各順列に対して符号の組み合わせを考慮
            for s_h in ([0] if p_abs[0] == 0 else [-1, 1]): # 0なら符号は1つだけ(0)
                for s_k in ([0] if p_abs[1] == 0 else [-1, 1]):
                    for s_l in ([0] if p_abs[2] == 0 else [-1, 1]):
                        # 符号を適用 (ただし、元の値が0なら結果も0)
                        h_signed = p_abs[0] * s_h if p_abs[0] != 0 else 0
                        k_signed = p_abs[1] * s_k if p_abs[1] != 0 else 0
                        l_signed = p_abs[2] * s_l if p_abs[2] != 0 else 0
                        
                        if h_signed == 0 and k_signed == 0 and l_signed == 0: # (0,0,0) は除く
                            continue
                        
                        current_hkl = (h_signed, k_signed, l_signed)
                        
                        # ラベル付け: 代表的な方位（ファミリーの最初のものや低指数のもの）に限定
                        label = None
                        # 正規化してソートしたタプルで、ファミリー内での代表点か判定
                        # (例: <100>なら (1,0,0) のみラベル、<110>なら(1,1,0)のみラベル)
                        # 簡単のため、代表インデックスの permutations のうち、符号がすべて正か、
                        # 元の代表インデックスに近いものにラベルを付ける
                        
                        # 元の代表指数そのもの、またはその符号違いや単純な軸入れ替えのみラベル表示
                        current_hkl_abs_sorted = tuple(sorted(map(abs, current_hkl)))
                        rep_indices_abs_sorted = tuple(sorted(map(abs, representative_indices)))

                        if current_hkl_abs_sorted == rep_indices_abs_sorted:
                            # さらに、ラベルを付ける対象を絞る（例：各ファミリーの代表的なもの数点）
                            # ここでは、元のインデックスの主要な対称操作によるものにラベルを付ける
                            key_for_label = tuple(sorted(current_hkl_abs_sorted)) # (0,0,1), (0,1,1), (1,1,1) etc.
                            if key_for_label not in seen_hkl_tuples_for_family_labeling:
                                seen_hkl_tuples_for_family_labeling[key_for_label] = 0
                            
                            # 各ファミリーから数個だけラベルを付ける（簡易的）
                            if seen_hkl_tuples_for_family_labeling[key_for_label] < (4 if sum(key_for_label)<=2 else 2) : # <100>,<110>は4点、他は2点程度
                                label = format_hkl_label_unicode(h_signed, k_signed, l_signed)
                                seen_hkl_tuples_for_family_labeling[key_for_label] +=1
                                current_alpha_factor = 1.0
                                current_size_factor = 1.0
                            else:
                                current_alpha_factor = 0.6
                                current_size_factor = 0.8

                        else: # ファミリーには属するが、ラベル付け対象外の多数の点
                            current_alpha_factor = 0.5
                            current_size_factor = 0.7


                        poles.append({
                            "hkl": current_hkl, 
                            "label": label,
                            "marker": marker, 
                            "color": color,
                            "markersize": 5 * size_f * current_size_factor, # マーカーサイズ調整
                            "alpha": 0.8 * current_alpha_factor # 透明度調整
                        })
    
    # 重複を削除 (hklタプル基準で)
    unique_poles_final = []
    seen_exact_hkls = set()
    for pole_info in poles:
        hkl_tuple = tuple(pole_info["hkl"])
        if hkl_tuple not in seen_exact_hkls:
            unique_poles_final.append(pole_info)
            seen_exact_hkls.add(hkl_tuple)
            
    return unique_poles_final