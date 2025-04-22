import streamlit as st
import json, os
from datetime import date, datetime, timedelta
from utils import insert_tender, get_all_tenders, get_filtered_tenders, get_tender_by_id, update_tender, delete_tender, upload_files

st.set_page_config(page_title='Javna Nabava V15', layout='wide')
st.markdown("""<style>
th {background-color:#005bac;color:white;}
table {width:100%;border-collapse:collapse;margin-bottom:1em;}
td,th {border:1px solid #ddd;padding:8px;text-align:left;}
</style>""", unsafe_allow_html=True)

# Session state
if 'edit_id' not in st.session_state: st.session_state.edit_id = None
if 'confirm_id' not in st.session_state: st.session_state.confirm_id = None

# Callbacks
def start_edit(i): st.session_state.edit_id = i
def ask_delete(i): st.session_state.confirm_id = i
def do_delete(): delete_tender(st.session_state.confirm_id); st.session_state.confirm_id = None

mode = st.sidebar.radio('Prikaz:', ['Guest pregled','Admin unos'], label_visibility='visible')

if mode == 'Admin unos':
    st.title('Admin - Unos i Uređivanje')
    # Add form
    with st.form('add_form', clear_on_submit=True):
        left, right = st.columns(2)
        with left:
            datum = st.date_input('Datum objave', date.today())
            naziv = st.text_input('Naziv predmeta nabave', key='add_naziv')
            cpv = st.number_input('CPV', min_value=1, format='%d', key='add_cpv')
        with right:
            doc = st.selectbox('Vrsta dokumenta', ['Odaberi','Bagatelna nabava','Izmjena dokumentacije za nadmetanje','Obavijest o početku postupka javne nabave','Obavijest o rezultatima natječaja','Obavijest o sklopljenim ugovorima','Objava o poništenju nadmetanja / ispravku objave','Objava o uspostavljanju kvalifikacijskog sustava','Pojednostavljena obavijest u dinamičkom sustavu nabave','Poziv na nadmetanje','Poziv na natječaj','Prethodna (indikativna) obavijest','PRODAJA'], key='add_doc')
            ug = st.selectbox('Vrsta ugovora', ['Odaberi','Isporuka robe','Javne usluge','Javni radovi','PRODAJA'], key='add_ug')
            post = st.selectbox('Vrsta postupka', ['Odaberi','Bagatelna nabava','Natječaj','Ograničeni postupak','Otvoreni postupak','Pregovarački postupak bez prethodne objave','Pregovarački postupak s prethodnom objavom','PRODAJA','Ugovori s povezanim Društvima','Usluge iz Dodatka II.B'], key='add_post')
        files = st.file_uploader('Prilozi', accept_multiple_files=True, type=['pdf','doc','docx','xls','xlsx'], key='add_files')
        submit = st.form_submit_button('Spremi')
        if submit:
            errors = []
            if not naziv: errors.append('Naziv')
            if cpv < 1: errors.append('CPV')
            if st.session_state.add_doc == 'Odaberi': errors.append('Dokument')
            if st.session_state.add_ug == 'Odaberi': errors.append('Ugovor')
            if st.session_state.add_post == 'Odaberi': errors.append('Postupak')
            if not st.session_state.add_files: errors.append('Prilozi')
            if errors:
                st.warning('Nedostaju: ' + ', '.join(errors))
            else:
                saved = upload_files(st.session_state.add_files)
                insert_tender(str(datum), naziv, st.session_state.add_doc, st.session_state.add_ug, st.session_state.add_post, st.session_state.add_cpv, saved)
                st.success('Podaci uspješno spremljeni!')

    # Edit form with prefill and validation
    if st.session_state.edit_id is not None:
        t = get_tender_by_id(st.session_state.edit_id)
        st.markdown('---')
        st.subheader('Uredi zapis')
        with st.form('edit_form', clear_on_submit=True):
            left, right = st.columns(2)
            with left:
                ed = st.date_input('Datum objave', datetime.strptime(t[1], '%Y-%m-%d').date(), key='edit_date')
                en = st.text_input('Naziv predmeta nabave', t[2], key='edit_naziv')
                ec = st.number_input('CPV', min_value=1, value=t[6], key='edit_cpv')
            with right:
                edoc = st.selectbox('Vrsta dokumenta', ['Odaberi','Bagatelna nabava','Izmjena dokumentacije za nadmetanje','Obavijest o početku postupka javne nabave','Obavijest o rezultatima natječaja','Obavijest o sklopljenim ugovorima','Objava o poništenju nadmetanja / ispravku objave','Objava o uspostavljanju kvalifikacijskog sustava','Pojednostavljena obavijest u dinamičkom sustavu nabave','Poziv na nadmetanje','Poziv na natječaj','Prethodna (indikativna) obavijest','PRODAJA'], index=['Odaberi','Bagatelna nabava','Izmjena dokumentacije za nadmetanje','Obavijest o početku postupka javne nabave','Obavijest o rezultatima natječaja','Obavijest o sklopljenim ugovorima','Objava o poništenju nadmetanja / ispravku objave','Objava o uspostavljanju kvalifikacijskog sustava','Pojednostavljena obavijest u dinamičkom sustavu nabave','Poziv na nadmetanje','Poziv na natječaj','Prethodna (indikativna) obavijest','PRODAJA'].index(t[3]), key='edit_doc')
                eug = st.selectbox('Vrsta ugovora', ['Odaberi','Isporuka robe','Javne usluge','Javni radovi','PRODAJA'], index=['Odaberi','Isporuka robe','Javne usluge','Javni radovi','PRODAJA'].index(t[4]), key='edit_ug')
                epost = st.selectbox('Vrsta postupka', ['Odaberi','Bagatelna nabava','Natječaj','Ograničeni postupak','Otvoreni postupak','Pregovarački postupak bez prethodne objave','Pregovarački postupak s prethodnom objavom','PRODAJA','Ugovori s povezanim Društvima','Usluge iz Dodatka II.B'], index=['Odaberi','Bagatelna nabava','Natječaj','Ograničeni postupak','Otvoreni postupak','Pregovarački postupak bez prethodne objave','Pregovarački postupak s prethodnom objavom','PRODAJA','Ugovori s povezanim Društvima','Usluge из Dodatка II.B'].index(t[5]), key='edit_post')
            new_files = st.file_uploader('Novi prilozi', accept_multiple_files=True, type=['pdf','doc','docx','xls','xlsx'], key='edit_files')
            sb, cb = st.columns(2)
            save_btn = sb.form_submit_button('Spremi izmjene')
            cancel_btn = cb.form_submit_button('Cancel')
        if save_btn or cancel_btn:
            if save_btn:
                errors = []
                if not st.session_state.edit_naziv: errors.append('Naziv')
                if st.session_state.edit_cpv < 1: errors.append('CPV')
                if st.session_state.edit_doc == 'Odaberi': errors.append('Dokument')
                if st.session_state.edit_ug == 'Odaberi': errors.append('Ugovor')
                if st.session_state.edit_post == 'Odaberi': errors.append('Postupak')
                current_pr = json.loads(t[7] or '[]')
                if not current_pr and not st.session_state.edit_files: errors.append('Prilozi')
                if errors:
                    st.warning('Nedostaju: ' + ', '.join(errors))
                else:
                    added = upload_files(st.session_state.edit_files) if st.session_state.edit_files else []
                    update_tender(t[0], str(st.session_state.edit_date), st.session_state.edit_naziv, st.session_state.edit_doc, st.session_state.edit_ug, st.session_state.edit_post, st.session_state.edit_cpv, current_pr + added)
                    st.success('Izmjene spremljene!')
            st.session_state.edit_id = None

    if st.session_state.edit_id is None:
        st.subheader('Pregled unesenih zapisa')
        hdr = ['ID','Datum objave','Naziv','Dokument','Ugovor','Postupak','CPV','Prilozi','Akcije']
        cols_h = st.columns([0.5,1,2,1,1,1,0.7,2,1])
        for i,h in enumerate(hdr): cols_h[i].markdown(f'**{h}**')
        for r in get_all_tenders():
            cols = st.columns([0.5,1,2,1,1,1,0.7,2,1])
            cols[0].write(r[0]); cols[1].write(r[1]); cols[2].write(r[2]); cols[3].write(r[3]); cols[4].write(r[4]); cols[5].write(r[5]); cols[6].write(r[6])
            pr = json.loads(r[7] or '[]')
            for idx,f in enumerate(pr):
                path = os.path.join('uploads', f)
                if os.path.exists(path):
                    cols[7].download_button(label=f, data=open(path,'rb').read(), file_name=f, key=f'dl_{r[0]}_{idx}')
                else:
                    cols[7].write(f'({f} ne postoji)')
            if st.session_state.confirm_id == r[0]:
                y,n = st.columns(2)
                if y.button('Da', key=f'yes_{r[0]}', on_click=do_delete): pass
                if n.button('Ne', key=f'no_{r[0]}'): st.session_state.confirm_id = None
            else:
                cols[8].button('Uredi', key=f'edit_{r[0]}', on_click=start_edit, args=(r[0],))
                cols[8].button('Obriši', key=f'del_{r[0]}', on_click=ask_delete, args=(r[0],))

elif mode == 'Guest pregled':
    st.title('Guest pregled')
    st.sidebar.title('Filteri')
    vd = st.sidebar.selectbox('Vrsta dokumenta', ['Odaberi','Bagatelna nabava','Izmjena dokumentacije za nadmetanje','Obavijest o početku postupka javne nabave','Obavijest o rezultatima natječaja','Obavijest o sklopljenim ugovorima','Objava o poništenju nadmetanja / ispravku objave','Objava o uspostavljanju kvalifikacijskog sustava','Pojednostavljena obavijest u dinamičkom sustavu nabave','Poziv na nadmetanje','Poziv na natječaj','Prethodna (indikativna) obavijest','PRODAJA'], key='g_vd')
    vu = st.sidebar.selectbox('Vrsta ugovora', ['Odaberi','Isporuka robe','Javne usluge','Javni radovi','PRODAJA'], key='g_vu')
    vp = st.sidebar.selectbox('Vrsta postupka', ['Odaberi','Bagatelna nabava','Natječaj','Ograničeni postupak','Otvoreni postupak','Pregovarački postupak bez prethodne objavom','PRODAЈА','Ugovori s povezanim Društima','Usluge iz Dodatka II.B'], key='g_vp')
    per = st.sidebar.selectbox('Period', ['Odaberi','Danas','Ovaj mjesec','Ova godina','Prošla godina','Od - Do'], key='g_per')
    today = date.today()
    from_date = to_date = None
    if per == 'Danas':
        from_date = to_date = today
    elif per == 'Ovaj mjesec':
        from_date = date(today.year, today.month, 1); to_date = today
    elif per == 'Ova godina':
        from_date = date(today.year, 1, 1); to_date = today
    elif per == 'Prošla godina':
        from_date = date(today.year-1, 1, 1); to_date = date(today.year-1, 12, 31)
    elif per == 'Od - Do':
        from_date = st.sidebar.date_input('Od', today - timedelta(days=30), key='g_od')
        to_date = st.sidebar.date_input('Do', today, key='g_do')
    cpv = st.sidebar.text_input('CPV', key='g_cpv')
    data = get_filtered_tenders(vd, vu, vp, str(from_date) if from_date else None, str(to_date) if to_date else None, cpv)
    st.subheader('Rezultati')
    hdr = ['Datum objave','Naziv','Dokument','Ugovor','Postupak','CPV','Prilozi']
    cols_h = st.columns([1,2,1,1,1,1,2])
    for i,h in enumerate(hdr): cols_h[i].markdown(f'**{h}**')
    for r in data:
        cols = st.columns([1,2,1,1,1,1,2])
        cols[0].write(r[1]); cols[1].write(r[2]); cols[2].write(r[3]); cols[3].write(r[4]); cols[4].write(r[5]); cols[5].write(r[6])
        pr = json.loads(r[7] or '[]')
        if pr:
            for idx,f in enumerate(pr):
                p = os.path.join('uploads', f)
                if os.path.exists(p):
                    with open(p,'rb') as fp: cols[6].download_button(label=f, data=fp.read(), file_name=f, key=f'gdl_{r[0]}_{idx}')
                else:
                    cols[6].write(f'({f} ne postoji)')
        else:
            cols[6].write('-')
