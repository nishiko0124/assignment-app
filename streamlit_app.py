# streamlit_app.py

import streamlit as st
import random
import math

# --- 設定 ---
INITIAL_MEMBERS = ["いとう", "さいとう", "さわ", "にしかわ"]
SUBJECTS = ["指定なし", "民法1", "民法2", "憲法", "刑法"] # 科目リスト
# ------------

# --- NEW: 担当数もランダムにする割り当て関数 ---
def assign_problems_random_counts(total_problems, member_list):
    """
    問題の割り当てをランダムに行い、かつ、
    割り切れない場合に誰が多く担当するか自体もランダムにする関数。
    """
    num_members = len(member_list)
    if num_members == 0: return {}
    if total_problems <= 0: return {member: [] for member in member_list}

    # 1. 各メンバーの基本担当数と、追加で担当するメンバー数を計算
    base_count = total_problems // num_members
    extra_count = total_problems % num_members # 何人が追加で1問担当するか

    # 2. 追加で1問担当するメンバーをランダムに選ぶ (重複なし)
    members_getting_extra = set(random.sample(member_list, extra_count))

    # 3. 全問題番号のリストを作成し、ランダムにシャッフル
    all_problem_numbers = list(range(1, total_problems + 1))
    random.shuffle(all_problem_numbers)

    # 4. 割り当てを実行
    assignments = {member: [] for member in member_list}
    problem_idx = 0 # シャッフルされたリストから次に割り当てる問題のインデックス

    for member in member_list:
        # このメンバーが追加担当者に選ばれているか？
        if member in members_getting_extra:
            num_to_assign = base_count + 1 # 基本数 + 1問を割り当て
        else:
            num_to_assign = base_count      # 基本数を割り当て

        # シャッフルされたリストから、割り当てるべき数の問題を取得
        end_idx = problem_idx + num_to_assign
        # リストの範囲外アクセスを防ぐ（万が一のため）
        end_idx = min(end_idx, total_problems)
        assigned_chunk = all_problem_numbers[problem_idx:end_idx]
        assignments[member] = assigned_chunk

        # 次の問題の開始インデックスを更新
        problem_idx = end_idx

    # 5. 各メンバーの担当問題リストを見やすくソート（任意）
    for member in assignments:
        assignments[member].sort()

    return assignments

# --- Streamlit アプリケーション部分 ---

st.set_page_config(page_title="課題割り振り君", layout="centered")
st.title("📝 予習課題 自動割り振りツール")

# --- メンバー設定 (折りたたみ) ---
st.subheader("メンバー設定")
if 'members_text' not in st.session_state:
    st.session_state['members_text'] = ", ".join(INITIAL_MEMBERS)

with st.expander("メンバーリストを表示/編集する", expanded=False):
    st.info("カンマ(,)区切りでメンバー名を入力・編集してください。")
    members_input_widget = st.text_area(
        "編集エリア:",
        value=st.session_state['members_text'],
        key="members_text_widget"
    )
    st.session_state['members_text'] = members_input_widget
    temp_members_check = [name.strip() for name in st.session_state['members_text'].split(',') if name.strip()]
    if not temp_members_check:
        st.warning("メンバーが入力されていません。")
    else:
        st.success(f"現在 {len(temp_members_check)} 名のメンバーが設定されています。")

# --- メンバー表示 (常に表示) ---
current_members = [name.strip() for name in st.session_state['members_text'].split(',') if name.strip()]
if not current_members:
    st.error("メンバーが設定されていません。上の「メンバーリストを表示/編集する」を開いて入力してください。")
else:
    st.write(f"**現在の割り当て対象メンバー ({len(current_members)}名):** {', '.join(current_members)}")

st.markdown("---")

# --- 科目選択と問題数入力 ---
st.subheader("割り当て設定")

# 科目選択を追加
selected_subject = st.selectbox(
    "科目を選択してください:",
    SUBJECTS,
    index=0 # デフォルトで "指定なし" を選択状態にする
)

total_problems_input = st.number_input(
    "総問題数を入力してください:",
    min_value=1,
    step=1,
    value=max(1, len(current_members) if current_members else 1)
)

# --- 割り当て実行ボタン ---
if st.button("🔄 割り当て実行", disabled=(not current_members)):
    if total_problems_input >= 1 and current_members:
        # 割り当てを実行 (担当数もランダムにする関数を呼び出す)
        final_assignments = assign_problems_random_counts(total_problems_input, current_members)

        # --- 結果表示 (各行の科目名プレフィックスは無し) ---
        st.subheader("🎉 課題割り当て結果")
        if not final_assignments:
             st.warning("割り当て対象のメンバーがいません。")
        else:
            # メンバー数に応じて列を分割 (メンバー数が少ない場合も考慮)
            num_columns = min(len(current_members), 4) # 例: 最大4列までにする
            cols = st.columns(num_columns)
            member_index = 0
            # メンバー名をソートして表示順を固定
            sorted_members = sorted(final_assignments.keys())

            for member in sorted_members:
                problems = final_assignments[member]
                # 列を順番に使う
                with cols[member_index % num_columns]:
                    if problems:
                        problem_str = ", ".join(map(str, problems))
                        st.markdown(f"**{member}** ({len(problems)}問)")
                        st.write(f"問題: {problem_str}") # 科目プレフィックスなし
                    else:
                        st.markdown(f"**{member}** (0問)")
                        st.write("担当なし")
                member_index += 1

            # --- 共有用テキスト生成と表示 ---
            st.divider() # 区切り線を追加
            st.subheader("📲 共有用テキスト")

            share_lines = []
            # ヘッダー行 (科目名を含む)
            if selected_subject != "指定なし":
                share_lines.append(f"【{selected_subject} 課題割り当て ({total_problems_input}問)】")
            else:
                share_lines.append(f"【課題割り当て ({total_problems_input}問)】")
            share_lines.append("---") # 区切り線

            # 各メンバーの割り当て（表示順と同じくソートされたメンバー順）
            for member in sorted_members:
                problems = final_assignments[member]
                if problems:
                    problem_str = ", ".join(map(str, problems))
                    share_lines.append(f"{member}さん: 問題 {problem_str} ({len(problems)}問)")
                else:
                    share_lines.append(f"{member}さん: 担当なし")

            share_text = "\n".join(share_lines) # 各行を改行で結合

            # st.code() で整形済みテキストとして表示
            st.code(share_text, language=None)
            st.info("上のテキストボックスの内容全体をコピーして、チャットなどに貼り付けて共有できます。")

            # (補足情報コメントアウト)
            #st.caption("※ より便利な「コピー」ボタンを設置するには、`streamlit-copy-button` などの追加ライブラリの導入が必要です。")
            # --- 共有用テキストここまで ---

    elif not current_members:
         st.error("メンバーリストが空です。メンバーを入力してください。")
    else:
         st.warning("問題数を1以上で入力してください。")

st.markdown("---")
st.caption("Powered by Streamlit")
