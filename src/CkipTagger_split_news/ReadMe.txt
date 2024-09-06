創建 anaconda 虛擬環境單獨執行斷詞程式碼
因 tensorflow 版本更新，為了配合 CkipTagger 版本出很多錯
關於較詳細的 CkipTagger 資訊以及 ckip_data 可於 https://github.com/ckiplab/ckiptagger 找到

conda create -n ckip anaconda python=3.9
pip install tensorflow==2.12.0 --upgrade
pip install gensim==4.3.0
pip install FuzzyTM>=0.4.0
pip install -U ckiptagger