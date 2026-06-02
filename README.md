# Meta Ads 数据分析看板

这是一个用于 Meta Ads Manager 导出数据的 Streamlit 分析应用。上传 CSV 或 Excel 后，会自动完成字段识别、数据清洗、每日聚合、趋势图、转化漏斗、广告层级排行和基础策略诊断。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 启动应用

```bash
streamlit run app.py
```

打开终端输出的本地地址，通常是 `http://localhost:8501`，然后上传 Meta 广告报表文件即可。

## 改动日志

每次功能更新都会记录在 `CHANGELOG.md`，其中包含改动标题和内容，可直接用于整理 commit message。

## 建议字段

- `报告开始日期`
- `已花费金额 (USD)`
- `展示次数`
- `覆盖人数`
- `CPM（千次展示费用） (USD)`
- `点击率（全部）`
- `点击量`
- `链接点击量`
- `落地页浏览量`
- `加入购物车次数`
- `结账发起次数`
- `成效`
- `广告花费回报 (ROAS) - 购物`

应用也兼容部分英文列名，例如 `Date`、`Amount spent (USD)`、`Impressions`、`Link clicks`、`Purchases`、`ROAS`。
