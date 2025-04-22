# streamlit_app.py

import streamlit as st
import random
import math # math.ceil を使うためにインポート

# --- 設定 ---
# メンバーリスト (Webアプリ上でも編集可能にする場合は、後述のコメントアウトを解除)
# ここで定義したものが初期値になります。
INITIAL_MEMBERS = ["いとう", "さいとう", "さわ", "にしかわ"]
# ------------

# (割り当て関数は前のコードからそのままコピー＆ペースト)
# 関数の内容は変更ありません
def assign_problems_with_random_remainder(total_problems, member_list):
    num_members = len(member_list)
    if num_members == 0: return {}
    if total_problems <= 0: return {member: [] for member in member_list}

    assignments = {member: [] for member in member_list}
    base_problems_per_member = total_problems // num_members
    problem_counter = 1

    for _ in range(base_problems_per_member):
        for member in member_list:
            if problem_counter <= total_problems:
                assignments[member].append(problem_counter)
                problem_counter += 1

    remainder_count = total_problems % num_members
    remainder_problems = list(range(problem_counter, total_problems + 1))

    if remainder_count > 0:
        # 安全策：万が一、余りの数がメンバー数を超えることはないはずだが、念のため
        actual_remainder_assignees_count = min(remainder_count, num_members)
        if actual_remainder_assignees_count > 0:
             remainder_assignees = random.sample(member_list, actual_remainder_assignees_count)
             for i in range(remainder_count):
                 # 担当者が足りなくなった場合（基本発生しないはず）はループを抜ける
                 if i >= len(remainder_assignees): break
                 problem_to_assign = remainder_problems[i]
                 assignee = remainder_assignees[i]
                 assignments[assignee].append(problem_to_assign)

    for member in assignments:
        assignments[member].sort()
    return assignments

# --- Streamlit アプリケーション ---

st.set_page_config(page_title="課題割り振り君", layout="centered") # ブラウザタブのタイトル設定
st.title("📝 予習課題 自動割り振りツール")

# --- メンバー設定 ---
st.subheader("メンバー設定")
# st.session_state を使って、入力状態を保持する
if 'members_text' not in st.session_state:
    st.session_state['members_text'] = ", ".join(INITIAL_MEMBERS)

members_text_input = st.text_area(
    "メンバーリスト (カンマ区切りで入力・編集してください):",
    value=st.session_state['members_text'],
    key="members_text_area" # key を指定すると再描画時に値が維持されやすい
)
# 入力されたテキストをリストに変換（空要素は除去）
current_members = [name.strip() for name in members_text_input.split(',') if name.strip()]

if not current_members:
    st.warning("メンバーが入力されていません。")
else:
    st.write(f"現在のメンバー ({len(current_members)}名): {', '.join(current_members)}")

st.markdown("---") # 区切り線

# --- 問題数入力と実行 ---
st.subheader("割り当て実行")
total_problems_input = st.number_input(
    "総問題数を入力してください:",
    min_value=1,  # 1問以上を入力
    step=1,       # 整数入力
    value=max(1, len(current_members)) # デフォルト値をメンバー数か1に設定
)

# 割り当て実行ボタン
if st.button("🔄 割り当て実行", disabled=(not current_members)): # メンバーがいないとボタンを押せない
    if total_problems_input >= 1 and current_members:
        # 割り当てを実行
        final_assignments = assign_problems_with_random_remainder(total_problems_input, current_members)

        # 結果を表示
        st.subheader("🎉 課題割り当て結果")
        if not final_assignments:
             st.warning("割り当て対象のメンバーがいません。")
        else:
            # 担当者ごとに表示
            cols = st.columns(len(current_members)) # メンバー数に応じて列を分割
            member_index = 0
            for member, problems in final_assignments.items():
                with cols[member_index % len(cols)]: # 列を順番に使う
                    if problems:
                        problem_str = ", ".join(map(str, problems))
                        st.markdown(f"**{member}さん** ({len(problems)}問)")
                        st.write(f"問題: {problem_str}")
                    else:
                        st.markdown(f"**{member}さん** (0問)")
                        st.write("担当なし")
                member_index += 1

            # 全員分を表示した後、リスト形式でも表示（オプション）
            # st.write("---")
            # st.write("リスト形式:")
            # for member, problems in final_assignments.items():
            #     if problems:
            #         problem_str = ", ".join(map(str, problems))
            #         st.write(f"- {member}さん: 問題 {problem_str}")
            #     else:
            #         st.write(f"- {member}さん: 担当なし")

    elif not current_members:
         st.error("メンバーリストが空です。メンバーを入力してください。")
    else:
         st.warning("問題数を1以上で入力してください。")

st.markdown("---")
st.caption(f"Powered by Streamlit | {st.experimental_get_query_params().get('timestamp', [''])[0]}") # ちょっとしたフッター
