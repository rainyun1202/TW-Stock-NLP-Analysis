請透過 Linux 環境執行該腳本，這裡以使用 WSL (Microsoft Windows Subsystem for Linux) Ubuntu 為範例：
電腦環境從未安裝過 WSL 時： (請使用系統管理員等級的 Powershell 安裝)
先使用 wsl --install 安裝 WSL 虛擬環境
wsl --list --verbose (查看目前電腦的 WSL 版本)
wsl --list --online (查看可用的版本清單)
執行 wsl --install -d <DistroName> 以安裝特定版本：
wsl --install Ubuntu-22.04

wsl -d Ubuntu-22.04 在 Powershll 啟動特定版本的 Ubuntu。

安裝 JAVA 到 Ubuntu：
sudo apt install default-jre
sudo apt install default-jdk

java -version (查看 JAVA 版本在 Ubuntu 的安裝狀態)

可能發生錯誤，可以透過以下方法嘗試解決： (sudo 相當於提供 Ubuntu 系統管理員權限)
sudo apt update && sudo apt upgrade
這兩個命令作用如下：
1. sudo apt update：用於更新套件源。它會檢查可用的軟件包清單，以確保系統知道所有最新的套件。
2. sudo apt upgrade：用於升級已安裝的套件。安裝可用的最新版本套件，並且提示是否要執行這些更新。

於 WSL Ubuntu 中設定路徑： (請將 copeopi_counting.7z 解壓縮後放入 CopeOpi_scripts，並將資料夾移至 Ubuntu 路徑下執行)
提供 CopeOpi 腳本與新聞資料 (.txt 檔案) 路徑 (即該 README 所在的資料夾路徑)：
cd /home/your_user_name/CopeOpi_scripts

在 Ubuntu 執行 CopeOpi 腳本計算新聞情緒分數：
bash ./run_ckip_news.sh (sudo bash ./run_ckip_news.sh)
bash ./run_trad.sh (中研院範例檔腳本，原程式碼泛用性不佳，可以先執行範例確認是否可以正常運作後再處理大量的新聞文本數據)

各個文檔之執行結果將會輸出到 out 資料夾中 (在此壓縮為 out.7z)，所有文檔的情緒分數則會輸出到 out.txt 檔案中 (取名為 copeopi_senti_score.txt 放置於 data)。