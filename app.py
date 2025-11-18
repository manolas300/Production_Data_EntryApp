# app.py — Streamlit CRUD με SQLite (ενημερωμένο με Pepper fields, L1-L27, Loss(h), L3/L8/L24/L25 comments)
import sqlite3
from contextlib import closing
from datetime import date
import pandas as pd
import streamlit as st

DB_PATH = "ari_production.db"

# -------------- DB --------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn

def init_db():
    with closing(get_conn()) as conn, conn, closing(conn.cursor()) as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rec_date   TEXT NOT NULL,         -- YYYY-MM-DD
            line       INTEGER NOT NULL,
            group_lines INTEGER NOT NULL,
            code       TEXT NOT NULL,         -- Κωδικός
            shift_start TEXT NOT NULL,        -- HH:MM
            shift_end   TEXT NOT NULL,        -- HH:MM
            filling_ws  INTEGER,              -- Filling WS
            catering    REAL,                 -- Catering (π.χ. 1.5, 2)

            code_tmx1   REAL DEFAULT 0,
            code_tmx2   REAL DEFAULT 0,
            code_tmx3   REAL DEFAULT 0,
            code_tmx4   REAL DEFAULT 0,
            code_tmx5   REAL DEFAULT 0,
            code_tmx6   REAL DEFAULT 0,

            
            control     INTEGER,              -- Control
            weighting   REAL,                 -- Weighting
            packaging   REAL,                 -- Packaging
            control_in_pack INTEGER,         -- Control in Packaging
            produced_pcs INTEGER,            -- Produced Pcs
            reworked_pcs INTEGER,            -- Reworked pcs
            wrong_weight_reworked INTEGER,   -- Wrong Weight (Reworked Pcs)
            destroyed   INTEGER,

            -- ΝΕΑ ΠΕΔΙΑ (από screenshots)
            red_pepper   REAL DEFAULT 0,
            green_pepper REAL DEFAULT 0,
            red_cherry_pepper REAL DEFAULT 0,
            snack_pepper REAL DEFAULT 0,
            yellow_cherry_pepper REAL DEFAULT 0,
            jalapeno REAL DEFAULT 0,
            stuffed_olives REAL DEFAULT 0,


            -- L1..L27 (ακέραια)
            l1  INTEGER DEFAULT 0,  l2  INTEGER DEFAULT 0,  l3  INTEGER DEFAULT 0,
            l4  INTEGER DEFAULT 0,  l5  INTEGER DEFAULT 0,  l6  INTEGER DEFAULT 0,
            l7  INTEGER DEFAULT 0,  l8  INTEGER DEFAULT 0,  l9  INTEGER DEFAULT 0,
            l10 INTEGER DEFAULT 0,  l11 INTEGER DEFAULT 0,  l12 INTEGER DEFAULT 0,
            l13 INTEGER DEFAULT 0,  l14 INTEGER DEFAULT 0,  l15 INTEGER DEFAULT 0,
            l16 INTEGER DEFAULT 0,  l17 INTEGER DEFAULT 0,  l18 INTEGER DEFAULT 0,
            l19 INTEGER DEFAULT 0,  l20 INTEGER DEFAULT 0,  l21 INTEGER DEFAULT 0,
            l22 INTEGER DEFAULT 0,  l23 INTEGER DEFAULT 0,  l24 INTEGER DEFAULT 0,
            l25 INTEGER DEFAULT 0,  l26 INTEGER DEFAULT 0,  l27 INTEGER DEFAULT 0,

            -- Comments
            l3_comment  TEXT,
            l8_comment  TEXT,
            l24_comment TEXT,
            l25_comment TEXT

        );
        """)
        c.execute("CREATE INDEX IF NOT EXISTS idx_prod_date ON production(rec_date);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_prod_line ON production(line);")

def insert_row(**kw):
    cols = ",".join(kw.keys())
    placeholders = ",".join(["?"]*len(kw))
    with closing(get_conn()) as conn, conn, closing(conn.cursor()) as c:
        c.execute(f"INSERT INTO production ({cols}) VALUES ({placeholders})", tuple(kw.values()))

def update_row(id_, **kw):
    sets = ",".join([f"{k}=?" for k in kw.keys()])
    with closing(get_conn()) as conn, conn, closing(conn.cursor()) as c:
        c.execute(f"UPDATE production SET {sets} WHERE id=?", (*kw.values(), id_))

def delete_row(id_):
    with closing(get_conn()) as conn, conn, closing(conn.cursor()) as c:
        c.execute("DELETE FROM production WHERE id=?", (id_,))

def fetch_rows(date_from=None, date_to=None, line=None):
    q = "SELECT * FROM production WHERE 1=1"
    p = []
    if date_from:
        q += " AND date(rec_date) >= date(?)"; p.append(date_from)
    if date_to:
        q += " AND date(rec_date) <= date(?)"; p.append(date_to)
    if line is not None and str(line).strip() != "":
        q += " AND line = ?"; p.append(int(line))
    q += " ORDER BY date(rec_date) DESC, id DESC"
    with closing(get_conn()) as conn:
        df = pd.read_sql_query(q, conn, params=p)
    return df

# -------------- UI --------------
import streamlit as st

st.set_page_config(page_title="ARI Production Entry", page_icon="🗂️", layout="wide")

# --- Header: πάνω εικόνα, από κάτω τίτλος ---
# (ανέβασε το πλάτος όπως θες: 220, 260, 300...)
st.image("ari_logo.png", width=250)            # ΠΑΝΩ η εικόνα
st.markdown("<h1 style='margin: 10px 0 6px 0;'>ARI Production</h1>", unsafe_allow_html=True)  # ΚΑΤΩ ο τίτλος

# προαιρετικά λίγο μικρότερο πάνω padding
st.markdown("""
<style>.block-container { padding-top: 4.0rem; }</style>
""", unsafe_allow_html=True)

# συνέχισε εδώ...
init_db()
tab_new, tab_view, tab_edit = st.tabs(["➕ Νέα καταχώριση", "📄 Προβολή & Φίλτρα", "✏️ Επεξεργασία / Διαγραφή"])


# -------------- Νέα καταχώριση --------------
with tab_new:
    st.subheader("Καταχώριση")
    with st.form("frm_new", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        rec_date   = c1.date_input("Date", value=date.today(), format="DD/MM/YYYY")
        line       = c2.number_input("Line", min_value=1, step=1, value=1)
        group_lines= c3.text_input("group of lines", value="1", placeholder="π.χ. 1")
        code       = c4.text_input("Κωδικός", placeholder="π.χ. 182524")

        c5, c6, c7, c8 = st.columns(4)
        shift_start = c5.text_input("Shift Start", value="07:30", placeholder="HH:MM")
        shift_end   = c6.text_input("Shift End", value="15:30", placeholder="HH:MM")
        filling_ws  = c7.number_input("Filling WS", min_value=0, step=1, value=0)
        catering    = c8.number_input("Catering", min_value=0.0, step=0.1, value=0.0)

        cc1, cc2, cc3, cc4, cc5, cc6 = st.columns(6)
        code_tmx1 = cc1.number_input("Κωδικός Τμχ 1", min_value=0.0, step=0.5, value=0.0)
        code_tmx2 = cc2.number_input("Κωδικός Τμχ 2", min_value=0.0, step=0.5, value=0.0)
        code_tmx3 = cc3.number_input("Κωδικός Τμχ 3", min_value=0.0, step=0.5, value=0.0)
        code_tmx4 = cc4.number_input("Κωδικός Τμχ 4", min_value=0.0, step=0.5, value=0.0)
        code_tmx5 = cc5.number_input("Κωδικός Τμχ 5", min_value=0.0, step=0.5, value=0.0)
        code_tmx6 = cc6.number_input("Κωδικός Τμχ 6", min_value=0.0, step=0.5, value=0.0)

        r1, r2, r3, r4 = st.columns(4)
        control     = r1.number_input("Control", min_value=0, step=1, value=0)
        weighting   = r2.number_input("Weighting", min_value=0.0, step=0.1, value=0.0)
        packaging   = r3.number_input("Packaging", min_value=0.0, step=0.1, value=0.0)
        control_in_pack = r4.number_input("Control in Packaging", min_value=0, step=1, value=0)

        s1, s2, s3, s4 = st.columns(4)
        produced_pcs = s1.number_input("Produced Pcs", min_value=0, step=1, value=0)
        reworked_pcs = s2.number_input("Reworked pcs", min_value=0, step=1, value=0)
        wrong_weight_reworked = s3.number_input("Wrong Weight (Reworked Pcs)", min_value=0, step=1, value=0)
        destroyed = s4.number_input("Destroyed", min_value=0, step=1, value=0)

        st.markdown("**Products**")
        p1,p2,p3,p4,p5,p6,p7 = st.columns(7)
        red_pepper   = p1.number_input("Red Pepper", min_value=0.0, step=0.5, value=0.0)
        green_pepper = p2.number_input("Green Pepper", min_value=0.0, step=0.5, value=0.0)
        red_cherry_pepper = p3.number_input("Red Cherry Pepper", min_value=0.0, step=0.5, value=0.0)
        snack_pepper = p4.number_input("Snack Pepper", min_value=0.0, step=0.5, value=0.0)
        yellow_cherry_pepper = p5.number_input("Yellow Cherry Pepper", min_value=0.0, step=0.5, value=0.0)
        jalapeno = p6.number_input("Jalapeno", min_value=0.0, step=0.5, value=0.0)
        stuffed_olives = p7.number_input("Stuffed Olives", min_value=0.0, step=0.5, value=0.0)


        st.markdown("**Errors**")
        # 27 πεδία σε 3 σειρές των 9
        L_vals = {}
        for rowstart in [1, 10, 19]:
            cols = st.columns(9)
            for i, col in enumerate(cols, start=rowstart):
                if i > 27: break
                L_vals[f"l{i}"] = col.number_input(f"L{i}", min_value=0, step=1, value=0, key=f"l{i}_new")

        st.markdown("**Comments**")
        cA,cB,cC,cD = st.columns(4)
        l3_comment  = cA.text_input("L3 comment")
        l8_comment  = cB.text_input("L8 comment")
        l24_comment = cC.text_input("L24 comment")
        l25_comment = cD.text_input("L25 comment")

        submitted = st.form_submit_button("Καταχώριση", use_container_width=True)
        if submitted:
            errors = []
            if not str(code).strip(): errors.append("Κωδικός")
            if not str(group_lines).strip() or not str(group_lines).strip().isdigit():
                errors.append("group of lines (πρέπει να είναι αριθμός)")
            for lbl, t in [("Shift Start", shift_start), ("Shift End", shift_end)]:
                if len(t.strip()) < 4 or ":" not in t: errors.append(lbl)
            if errors:
                st.error("Έλεγξε τα πεδία: " + ", ".join(errors))
            else:
                payload = dict(
                    rec_date=rec_date.isoformat(),
                    line=int(line),
                    group_lines=int(group_lines),
                    code=code.strip(),
                    shift_start=shift_start.strip(),
                    shift_end=shift_end.strip(),
                    filling_ws=int(filling_ws),
                    catering=float(catering),
                    code_tmx1=float(code_tmx1),
                    code_tmx2=float(code_tmx2),
                    code_tmx3=float(code_tmx3),
                    code_tmx4=float(code_tmx4),
                    code_tmx5=float(code_tmx5),
                    code_tmx6=float(code_tmx6),
                    control=int(control),
                    weighting=float(weighting),
                    packaging=float(packaging),
                    control_in_pack=int(control_in_pack),
                    produced_pcs=int(produced_pcs),
                    reworked_pcs=int(reworked_pcs),
                    wrong_weight_reworked=int(wrong_weight_reworked),
                    destroyed=int(destroyed),
                    red_pepper=float(red_pepper),
                    green_pepper=float(green_pepper),
                    red_cherry_pepper=float(red_cherry_pepper),
                    snack_pepper=float(snack_pepper),
                    yellow_cherry_pepper=float(yellow_cherry_pepper),
                    jalapeno=float(jalapeno),
                    stuffed_olives=float(stuffed_olives),
                    l3_comment=l3_comment.strip() or None,
                    l8_comment=l8_comment.strip() or None,
                    l24_comment=l24_comment.strip() or None,
                    l25_comment=l25_comment.strip() or None,
                )
                payload.update({k:int(v) for k,v in L_vals.items()})
                insert_row(**payload)
                st.success("✅ Η καταχώριση αποθηκεύτηκε.")

# -------------- Προβολή & Φίλτρα --------------
with tab_view:
    st.subheader("Πίνακας εγγραφών")
    f1, f2, f3 = st.columns(3)
    date_from = f1.date_input("Από", value=None, format="DD/MM/YYYY")
    date_to   = f2.date_input("Έως", value=None, format="DD/MM/YYYY")
    f_line    = f3.number_input("Line (φίλτρο)", min_value=0, step=1, value=0, help="0 = χωρίς φίλτρο")
    df = fetch_rows(date_from.isoformat() if date_from else None,
                    date_to.isoformat() if date_to else None,
                    None if f_line==0 else f_line)
    st.caption(f"Βρέθηκαν {len(df)} εγγραφές.")
    st.dataframe(df, use_container_width=True, hide_index=True)

    cx1, cx2 = st.columns(2)
    if cx1.button("🔄 Ανανέωση", use_container_width=True):
        st.rerun()
    cx2.download_button("⬇️ Export CSV", data=df.to_csv(index=False).encode("utf-8"),
                        file_name="production.csv", mime="text/csv", use_container_width=True)

# -------------- Επεξεργασία / Διαγραφή --------------
with tab_edit:
    st.subheader("Επιλογή εγγραφής")
    df_all = fetch_rows()
    if df_all.empty:
        st.info("Δεν υπάρχουν εγγραφές για επεξεργασία.")
    else:
        df_all["label"] = df_all.apply(lambda r: f"#{r['id']} | {r['rec_date']} | L{r['line']} | {r['code']} | pcs={r['produced_pcs']}", axis=1)
        pick = st.selectbox("Διάλεξε εγγραφή", options=df_all["id"].tolist(),
                            format_func=lambda _id: df_all.loc[df_all["id"]==_id, "label"].values[0])

        rec = df_all[df_all["id"]==pick].iloc[0].to_dict()
        eA, eB = st.columns(2)
        mode = eA.radio("Ενέργεια", ["Επεξεργασία", "Διαγραφή"], horizontal=True)
        confirm = eB.toggle("Επιβεβαίωση", value=False)

        if mode == "Επεξεργασία":
            with st.form("frm_edit"):
                # ίδια πεδία με την καταχώριση
                c1, c2, c3, c4 = st.columns(4)
                rec_date   = c1.date_input("Date", value=pd.to_datetime(rec["rec_date"]).date(), format="DD/MM/YYYY")
                line       = c2.number_input("Line", min_value=1, step=1, value=int(rec["line"]))
                group_lines= c3.text_input("group of lines", value=str(rec["group_lines"]))
                code       = c4.text_input("Κωδικός", value=str(rec["code"]))

                c5, c6, c7, c8 = st.columns(4)
                shift_start = c5.text_input("Shift Start", value=str(rec["shift_start"]))
                shift_end   = c6.text_input("Shift End",   value=str(rec["shift_end"]))
                filling_ws  = c7.number_input("Filling WS", min_value=0, step=1, value=int(rec["filling_ws"] or 0))
                catering    = c8.number_input("Catering", min_value=0.0, step=0.1, value=float(rec["catering"] or 0.0))

                cc1, cc2, cc3, cc4, cc5, cc6 = st.columns(6)
                code_tmx1 = cc1.text_input("Κωδικός Τμχ 1", value=str(rec["code_tmx1"] or ""))
                code_tmx2 = cc2.text_input("Κωδικός Τμχ 2", value=str(rec["code_tmx2"] or ""))
                code_tmx3 = cc3.text_input("Κωδικός Τμχ 3", value=str(rec["code_tmx3"] or ""))
                code_tmx4 = cc4.text_input("Κωδικός Τμχ 4", value=str(rec["code_tmx4"] or ""))
                code_tmx5 = cc5.text_input("Κωδικός Τμχ 5", value=str(rec["code_tmx5"] or ""))
                code_tmx6 = cc6.text_input("Κωδικός Τμχ 6", value=str(rec["code_tmx6"] or ""))

                r1, r2, r3, r4 = st.columns(4)
                control     = r1.number_input("Control", min_value=0, step=1, value=int(rec["control"] or 0))
                weighting   = r2.number_input("Weighting", min_value=0.0, step=0.1, value=float(rec["weighting"] or 0.0))
                packaging   = r3.number_input("Packaging", min_value=0.0, step=0.1, value=float(rec["packaging"] or 0.0))
                control_in_pack = r4.number_input("Control in Packaging", min_value=0, step=1, value=int(rec["control_in_pack"] or 0))

                s1, s2, s3, s4 = st.columns(4)
                produced_pcs = s1.number_input("Produced Pcs", min_value=0, step=1, value=int(rec["produced_pcs"] or 0))
                reworked_pcs = s2.number_input("Reworked pcs", min_value=0, step=1, value=int(rec["reworked_pcs"] or 0))
                wrong_weight_reworked = s3.number_input("Wrong Weight (Reworked Pcs)", min_value=0, step=1, value=int(rec["wrong_weight_reworked"] or 0))
                destroyed = s4.number_input("Destroyed", min_value=0, step=1, value=int(rec["destroyed"] or 0))

                st.markdown("**Peppers / Products**")
                p1,p2,p3,p4,p5,p6,p7 = st.columns(7)
                red_pepper   = p1.number_input("Red Pepper", min_value=0.0, step=0.5, value=float(rec.get("red_pepper",0) or 0))
                green_pepper = p2.number_input("Green Pepper", min_value=0.0, step=0.5, value=float(rec.get("green_pepper",0) or 0))
                red_cherry_pepper = p3.number_input("Red Cherry Pepper", min_value=0.0, step=0.5, value=float(rec.get("red_cherry_pepper",0) or 0))
                snack_pepper = p4.number_input("Snack Pepper", min_value=0.0, step=0.5, value=float(rec.get("snack_pepper",0) or 0))
                yellow_cherry_pepper = p5.number_input("Yellow Cherry Pepper", min_value=0.0, step=0.5, value=float(rec.get("yellow_cherry_pepper",0) or 0))
                jalapeno = p6.number_input("Jalapeno", min_value=0.0, step=0.5, value=float(rec.get("jalapeno",0) or 0))
                stuffed_olives = p7.number_input("Stuffed Olives", min_value=0.0, step=0.5, value=float(rec.get("stuffed_olives",0) or 0))


                st.markdown("**L1 – L27**")
                L_vals = {}
                for rowstart in [1,10,19]:
                    cols = st.columns(9)
                    for i, col in enumerate(cols, start=rowstart):
                        if i > 27: break
                        key = f"l{i}"
                        L_vals[key] = col.number_input(f"L{i}", min_value=0, step=1, value=int(rec.get(key,0) or 0), key=f"{key}_edit")

                st.markdown("**Comments**")
                cA,cB,cC,cD = st.columns(4)
                l3_comment  = cA.text_input("L3 comment",  value=str(rec.get("l3_comment") or ""))
                l8_comment  = cB.text_input("L8 comment",  value=str(rec.get("l8_comment") or ""))
                l24_comment = cC.text_input("L24 comment", value=str(rec.get("l24_comment") or ""))
                l25_comment = cD.text_input("L25 comment", value=str(rec.get("l25_comment") or ""))

                do_update = st.form_submit_button("💾 Αποθήκευση αλλαγών", use_container_width=True, disabled=not confirm)
                if do_update:
                    if not code.strip():
                        st.error("Συμπλήρωσε τον Κωδικό.")
                    elif not str(group_lines).strip() or not str(group_lines).strip().isdigit():
                        st.error("Το group of lines πρέπει να είναι αριθμός.")
                    else:
                        payload = dict(
                            rec_date=rec_date.isoformat(),
                            line=int(line), group_lines=int(group_lines), code=code.strip(),
                            shift_start=shift_start.strip(), shift_end=shift_end.strip(),
                            filling_ws=int(filling_ws), catering=float(catering),
                            code_tmx1=code_tmx1.strip() or None, code_tmx2=code_tmx2.strip() or None,
                            code_tmx3=code_tmx3.strip() or None, code_tmx4=code_tmx4.strip() or None,
                            code_tmx5=code_tmx5.strip() or None, code_tmx6=code_tmx6.strip() or None,
                            weighting=float(weighting), packaging=float(packaging),
                            control_in_pack=int(control_in_pack),
                            produced_pcs=int(produced_pcs), reworked_pcs=int(reworked_pcs),
                            wrong_weight_reworked=int(wrong_weight_reworked), destroyed=int(destroyed),
                            red_pepper=float(red_pepper), green_pepper=float(green_pepper),
                            red_cherry_pepper=float(red_cherry_pepper), snack_pepper=float(snack_pepper),
                            yellow_cherry_pepper=float(yellow_cherry_pepper), jalapeno=float(jalapeno),
                            stuffed_olives=float(stuffed_olives),
                            l3_comment=l3_comment.strip() or None,
                            l8_comment=l8_comment.strip() or None,
                            l24_comment=l24_comment.strip() or None,
                            l25_comment=l25_comment.strip() or None
                        )
                        payload.update({k:int(v) for k,v in L_vals.items()})
                        update_row(int(rec["id"]), **payload)
                        st.success("✅ Η εγγραφή ενημερώθηκε.")
                        st.rerun()
        else:
            st.warning("Προσοχή: Η διαγραφή είναι οριστική.")
            if st.button("🗑️ Διαγραφή", type="primary", disabled=not confirm, use_container_width=True):
                delete_row(int(rec["id"]))
                st.success("🗑️ Η εγγραφή διαγράφηκε.")
                st.rerun()
