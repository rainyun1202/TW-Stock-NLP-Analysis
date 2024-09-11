
# TW-Stock-NLP-Analysis

## 簡介

結合網路爬蟲與資料清洗；自然語言處理、機器學習與財務數據分析。
透過爬取鉅亨網台股標籤之新聞，對新聞文本進行情緒分析與計算情緒分數，
並結合總體經濟變數與道瓊工業指數嘗試預測台灣加權股價指數（TAIEX）之報酬率，
進行回測與機器學習之漲跌預測。

### 情緒分析之基礎與參考文獻

投資者的買賣行為受一系列情緒與主觀認知等心理因素影響，在股市極度貪婪時過度買進，
或在股市持續低迷時恐慌拋售，導致資產價格偏離其內在價值，同時造成股價過度波動的現象。
投資者也會被股價的歷史高點或整數價格所錨定，並根據這些價格進行買賣決策。
- [Tetlock (2007)](references/2007_Tetlock_JF.pdf)
- [Jun Li & Jianfeng Yu (2012)](references/2012_Li_Yu_JFE.pdf)
- [García (2013)](references/2013_Garcia_JF.pdf)

## 專案結構圖

```bash
TW-Stock-NLP-Analysis/
│
├── data
│   ├── anue_news_data/
│   ├── binary_ml_result/
│   ├── HanLP_dataset/
│   ├── macro_var/
│   ├── senti_dict/
│   ├── TAIEX/
│   ├── ... other data
├── latex_table/
├── references/
├── src
│   ├── __init__.py
│   ├── anue_data_preparing
│   │   ├── __init__.py
│   │   ├── anue_scraper.log
│   │   ├── anue_scraper.py
│   │   └── clean_news_data.py
│   ├── CkipTagger_split_news
│   │   ├── CkipTagger使用範例.py
│   │   ├── CkipTagger與Jieba效能比較.pdf
│   │   ├── news_to_copeopi_script.py
│   │   ├── split_news.log
│   │   ├── split_news.py
│   │   └── 斷詞詞性解釋
│   │       ├── Entity_Types.xlsx
│   │       └── POS_Tags.xlsx
│   ├── CopeOpi_scripts
│   │   ├── CopeOpi_trad.class
│   │   ├── CopeOpi_trad.java
│   │   ├── ckip_to_cope_list.lst
│   │   ├── dic_trad
│   │   │   ├── neg_unigram.txt
│   │   │   ├── negation.txt
│   │   │   ├── negative_new.txt
│   │   │   ├── pos_unigram.txt
│   │   │   └── positive_new.txt
│   │   ├── file_trad.lst
│   │   ├── opinion
│   │   │   ├── OpinionCore_Enhanced.jar
│   │   │   ├── OpinionCore_Enhanced_simp.class
│   │   │   ├── OpinionCore_Enhanced_simp.jar
│   │   │   ├── OpinionCore_Enhanced_trad.class
│   │   │   └── OpinionCore_Enhanced_trad.jar
│   │   ├── run_ckip_news.sh
│   │   ├── run_trad.sh
│   │   ├── test_trad.txt
│   │   └── 請把所有新聞文本的 .txt 與 .lst 檔案都放在這裡.txt
│   ├── HanLP
│   │   ├── __init__.py
│   │   ├── booking_data_cleaning.py
│   │   └── hanlp_senti_plus_cope.py
│   ├── data_processing
│   │   ├── __init__.py
│   │   ├── __pycache__/
│   │   ├── add_djia_in_df.py
│   │   ├── create_lagged_features.py
│   │   ├── create_reg_vars.py
│   │   └── standardize_column.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── format_reg_model.py
│   │   ├── format_significance.py
│   │   ├── run_ols_and_format.py
│   │   └── stepwise_forward_selection.py
│   ├── scripts
│   │   ├── __init__.py
│   │   ├── (0) journal_senti_score.py
│   │   ├── (1) daily_data_preparing.py
│   │   ├── (2) daily_data_preparing_2.py
│   │   ├── (3) daily_return_analyze.py
│   │   ├── (4) daily_return_analyze_2.py
│   │   ├── binary_ML.py
│   │   └── investment_strategy.py
│   └── utils
│       ├── __init__.py
│       ├── calculate_ml_aic_bic.py
│       ├── generate_latex_table.py
│       ├── get_model_vars_df.py
│       └── ml_train_test_split.py
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
```

## 鉅亨網台股相關新聞爬蟲

抓取 2013 年初至 2022 年底的新聞數據並進行資料清洗，腳本位置在 /src/anue_data_preparing 下。  
由於抓取期間的原始新聞檔案約為 30 萬篇，進行清洗與斷詞後的檔案皆較龐大，
關於本 Repo 後續所需的大型數據文件皆可於 [此處下載](https://1drv.ms/f/s!AjbizXOpCs2kgodJ8qiV1D9q-0HjRg?e=qqsU9L)。  
每個 .zip 檔案都對照相應的數據路徑，並且按照 data 資料夾結構進行組織。

- `anue_news_data.zip`：包含 2013 年初至 2022 年底的原始新聞數據、乾淨新聞數據集與 CkipTagger 斷詞後所有符合 CopeOpi 腳本格式的新聞文本。
- `copeopi_counting.zip`：CopeOpi 腳本讀取的各篇新聞 .txt 檔案與 .lst 檔案。
- `out.zip`：執行 CopeOpi 腳本後的所有輸出結果。

將資料儲存在 data 對應的資料夾中即可執行程式碼。

## 透過 CkipTagger 進行新聞文本斷詞處理

透過 /src/CkipTagger_split_news 內的腳本完成，可以參考 [CkipTagger GitHub](https://github.com/ckiplab/ckiptagger)，
或我的範例檔案。

### 創建 Anaconda 虛擬環境執行斷詞程式碼：

```bash
conda create -n ckip_env anaconda python=3.9
pip install tensorflow==2.12.0 --upgrade
pip install gensim==4.3.0
pip install FuzzyTM>=0.4.0
pip install -U ckiptagger
```

## 使用 CopeOpi、HanLP 與字典匹配方法計算新聞情緒分數

### CopeOpi

腳本位於 /src/CopeOpi_scripts 中。  
參考文獻：
- [CSentiPackage](references/CSentiPackage官方文檔.pdf)
- [CopeOpi](references/2009_Ku_et_al_CopeOpi.pdf)

請透過 Linux 環境執行該腳本，這裡以使用 WSL (Microsoft Windows Subsystem for Linux) Ubuntu 為範例：  
電腦環境從未安裝過 WSL 時： (請使用系統管理員等級的 Powershell 安裝)  

```bash
# 安裝 WSL 虛擬環境
wsl --install
# 查看可用的版本清單
wsl --list --online
# 執行 wsl --install -d <DistroName> 以安裝特定版本 Ubuntu
wsl --install Ubuntu-22.04
# 查看目前裝置的 WSL 版本
wsl --list --verbose
# 在 Powershll 啟動特定版本的 Ubuntu
wsl -d Ubuntu-22.04
```

安裝 JAVA 到 Ubuntu：

```bash
sudo apt install default-jre
sudo apt install default-jdk

# 可查看 JAVA 版本在 Ubuntu 的安裝狀態
java -version
```

可能發生錯誤，可以透過該指令嘗試解決：

```bash
sudo apt update && sudo apt upgrade
```

作用如下：
1. sudo apt update：用於更新套件源。它會檢查可用的軟件包清單，以確保系統知道所有最新的套件。
2. sudo apt upgrade：用於升級已安裝的套件。安裝可用的最新版本套件，並且提示是否要執行這些更新。

於 WSL Ubuntu 中設定路徑：  
(請於 [此處下載](https://1drv.ms/f/s!AjbizXOpCs2kgodJ8qiV1D9q-0HjRg?e=qqsU9L) 檔案後，
將 copeopi_counting.7z 解壓縮後放入 CopeOpi_scripts，並將資料夾移至 Ubuntu 路徑下執行)。  
於 WSL Ubuntu 中提供 CopeOpi 腳本與新聞資料 (.txt 檔案) 路徑：

```bash
cd /home/your_user_name/CopeOpi_scripts
```

在 Ubuntu 執行 CopeOpi 腳本計算新聞情緒分數：
```bash
bash ./run_ckip_news.sh
# 若權限不足則執行 sudo bash ./run_ckip_news.sh

# 中研院範例檔腳本，原程式碼泛用性不佳，可以先執行範例確認是否可以正常運作後再處理大量的新聞文本數據
bash ./run_trad.sh
```

各個文檔之執行結果將會輸出到 out 資料夾中 (在此壓縮為 out.zip)，  
所有文檔的情緒分數則會輸出到 out.txt 檔案中 (在此取名為 copeopi_senti_score.txt 置於 data 中)。

### HanLP

參考：[pyhanlp](https://github.com/hankcs/pyhanlp)，  
相關程式碼位於 /src/HanLP 中。  
/data/HanLP_dataset 下提供使用 Booking 飯店評論資料集自製的訓練文本與 HanLP 提供的語料庫。  
參考：[HanLP GitHub](https://github.com/hankcs/HanLP)，  
建議創建一個新的 conda 環境來單獨執行 HanLP 分數計算之程式碼。  
Booking 飯店評論資料集 (booking_sentiment_dataset.zip) 解壓縮後須自行放置於 pyhanlp 路徑下，
若使用 conda 環境建置，路徑應位於：

```bash
C/Users/User/AppData/Local/anaconda3/envs/hanlp_env/Lib/site-packages/pyhanlp/static/data/test/my_sentiment_dataset
```

### 字典匹配

參考 [陳冠臻等人 (2020)](references/2020_陳冠臻_et_al_人文及社會科學集刊.pdf) 於人文及社會科學集刊發表之期刊，
根據該期刊自製之財經領域詞典與增廣意見詞詞典 (ANTUSD) 對斷詞後的新聞文本進行匹配以計算情緒分數，
程式碼位於 /src/scripts/`(0) journal_senti_score.py`

## 機器學習與回測結果

相關程式碼皆可於 /src/scripts 中找到，  
該專案證實了【當期】新聞情緒之有效性，然而【前一期 (日)】之新聞情緒則不具解釋與預測能力 (無法透過前進選擇法被 AIC 所挑出)，  
且台灣加權股票指數高度受美國股市所牽動，當機器學習模型放入前一期 (日) 美股指數時，機器學習模型預測正確率皆可達 6 成以上，  
但因股票市場存在跳空高開或低開之缺口，即使利用美股指數正確預測了隔日台股的漲跌，台股隨即就在開盤時出現缺口而提前反應完畢，
因此能透過交易獲取的超額報酬僅有開盤價至收盤價的差額 (這裡假定沒有在盤中相對高低點進行買賣交易)。  
在尚未考慮交易成本時 (手續費與證交稅)，通過十次模型的平均預測結果 (回測，分為三個不同測試集，詳細可以參考 scripts 內的程式碼) 可以穩定營利，
一旦納入交易成本時則虧損嚴重，顯示股票市場主動交易與策略交易之難處。  
如同【持續買進】一書所述，長期看好一個標的並不帶情緒不停地固定買進，或許才是散戶投資可行的長久獲利之道。  
本專案作為十分簡易股票市場回測與情緒分析之啟發，後續我將會繼續深入製作逐日更新的即時股票資訊與情緒分數，創建更多投資策略。  
