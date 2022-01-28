import streamlit as st
import pandas as pd 

st.title("Automation of STATEMENT worksheet")

@st.cache
def clean_data(data):
    import pandas as pd
    file = pd.read_excel(data,sheet_name='STATEMENT',usecols=['Transaction Type',
                                                                    'Transaction Amount',
                                                                    'BAI Description',
                                                                   'Text'])
    clean_amount=[]
    for i in file['Transaction Amount'].values:
        i=str(i).replace("(",'').replace(")",'').replace("$",'')
        clean_amount.append(float(i))
    
    file["Transaction Amount"] = clean_amount
  
    clean_txt=[]
    for i in file["Text"]:
        i = str(i)[16::].replace(" ",'')[5::]
        clean_txt.append(i)
    
    file["Text"] = clean_txt
    
    file = file[(file['Transaction Type'] != 'LEDGER') & (file['Transaction Type'] != 'OTHER')]
    file.dropna(inplace=True)
    return file


@st.cache
def get_result(data, beginning_balance):
    
    g1 = data.groupby(['Transaction Type','Text','BAI Description'], as_index=False)["Transaction Amount"].sum()
    total_credit = round(g1[g1['Transaction Type']=='CREDIT']['Transaction Amount'].sum(), 2)
    total_debit = round(g1[g1['Transaction Type']=='DEBIT']['Transaction Amount'].sum(), 2)
    ending_balance = beginning_balance + total_credit - total_debit
    
    return(f'''RESULT SUMMARY:
    "--------------------------------------
    
    Total Credit = {total_credit}
    ---------------------------------------
    Total Debit = {total_debit}
    ---------------------------------------
    Ending Balance = {round(ending_balance,2)}
    \n\n
    ''')


@st.cache
def disp_frame(data):
    result= data.groupby(['Transaction Type','Text','BAI Description'])["Transaction Amount"].sum().rename_axis(["Transaction Type",
                                                                                                    "Text",
                                                                                                    "Summary"]).to_frame()
    return result

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

@st.cache
def get_opening_balance(file_name):
    data = pd.read_excel(file_name,sheet_name='STATEMENT')
    return data[data["BAI Description"]=='OPENING LEDGER BALANCE']["Summary"].to_list()[0]


form = st.form(key='my_form')

review = form.text_input(label='Please input the data name or data path:')
submit = form.form_submit_button(label='click here to get result')

beginn = get_opening_balance(review)

if submit:
    data = clean_data(review)

    final_result = get_result(data,beginn)
    display = disp_frame(data)

    st.header("Output")

    st.write(final_result)
    st.write(display)


    csv = convert_df(display)

    st.download_button(
        label = "Download this output as CSV",
        data = csv,
        mime = 'text/csv'
    )