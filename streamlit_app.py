# streamlit_app.py

import streamlit as st
import random
import math

# --- 設定 ---
INITIAL_MEMBERS = ["いとう", "さいとう", "さわ", "にしかわ"]
SUBJECTS = ["指定なし", "民法1", "民法2", "憲法", "刑法"] # 科目リストを追加
# ------------

# --- 割り当て関数 (変更なし) ---
def assign_problems_fully_random(total_problems, member_list):
    # ... (この関数のコードは前のまま) ...
    num_members = len(member_list)
    if num_members == 0: return {}
    if total_problems <= 0: return {member: [] for member in member_list}
    all_problem_numbers = list(range(1, total_problems + 1))
    random.shuffle(all_problem_numbers)
    assignments = {member: [] for member in member_list}
    for i in range(total_problems):
        assignee_index = i % num_members
        assignee = member_list[assignee_index]
        problem_to_assign = all_problem_numbers[i]
        assignments[assignee].append(problem_to_assign)
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

# NEW: 科目選択を追加
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
        # 割り当てを実行
        final_assignments = assign_problems_fully_random(total_problems_input, current_members)

        # --- 結果表示 (科目名を追加) ---
        st.subheader("🎉 課題割り当て結果")
        if not final_assignments:
             st.warning("割り当て対象のメンバーがいません。")
        else:
            cols = st.columns(len(current_members))
            member_index = 0
            # メンバー名をソートして表示順を固定
            sorted_members = sorted(final_assignments.keys())

            for member in sorted_members:
                problems = final_assignments[member]
                with cols[member_index % len(cols)]:
                    # 科目名をプレフィックスとして追加
                    #subject_prefix = f"【{selected_subject}】 " if selected_subject != "指定なし" else ""

                    if problems:
                        problem_str = ", ".join(map(str, problems))
                        st.markdown(f"**{member}** ({len(problems)}問)")
                        st.write(f"問題: {problem_str}") # 科目名を追加
                    else:
                        st.markdown(f"**{member}** (0問)")
                        st.write("担当なし")
                member_index += 1

            # --- NEW: 共有用テキスト生成と表示 ---
            st.divider() # 区切り線を追加
            st.subheader("📲 共有用テキスト")

            share_lines = []
            # ヘッダー行
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

            # (補足情報)
            #st.caption("※ より便利な「コピー」ボタンを設置するには、`streamlit-copy-button` などの追加ライブラリの導入が必要です。")
            # --- 共有用テキストここまで ---

    elif not current_members:
         st.error("メンバーリストが空です。メンバーを入力してください。")
    else:
         st.warning("問題数を1以上で入力してください。")

st.markdown("---")
st.caption("Powered by Streamlit")
