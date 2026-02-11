import os
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# --- 1. データモデル (設計書 v2.1 に基づく統合データ) ---
# [cite: 91, 701, 702, 777-796]
facilities = [
    {
        "id": "shop-001",
        "name": "海の見える温泉宿 1",
        "category": "宿泊施設",
        "status": "営業中",
        "images": [
            "https://via.placeholder.com/600x400?text=Hotel_View_1",
            "https://via.placeholder.com/600x400?text=Room_View_2"
        ],
        "message": "元気に営業再開しました！応援よろしくお願いします。",
        "recommendation": "展望露天風呂と地魚の会席料理",
        "ec_url": "https://example.com",
        "map_url": "https://goo.gl/maps/example",
        "views": 1248
    },
    {
        "id": "shop-002",
        "name": "わんわん水族館",
        "category": "観光施設",
        "status": "準備中",
        "images": [
            "https://via.placeholder.com/600x400?text=Aquarium_Main"
        ],
        "message": "イルカショーも再開！笑顔をお届けします。",
        "recommendation": "イルカのふれあい体験",
        "ec_url": "#",
        "map_url": "https://goo.gl/maps/example2",
        "views": 850
    }
]

# --- 2. 統合UI (HTML/React/Tailwind CSS) ---
# [cite: 103-125, 799-838]
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>災害復興支援ポータル v2.1</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap');
        body { font-family: 'Noto Sans JP', sans-serif; }
    </style>
</head>
<body class="bg-slate-50">
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect } = React;

        const Icon = ({ name, className }) => {
            useEffect(() => { if (window.lucide) window.lucide.createIcons(); }, [name]);
            return <i data-lucide={name} className={className}></i>;
        };

        const App = () => {
            const [data] = useState({{ facilities | tojson }});
            const [filter, setFilter] = useState("すべて");
            const categories = ["すべて", "おみやげ", "食堂", "宿泊施設", "観光施設", "その他"];

            const filteredData = filter === "すべて" 
                ? data 
                : data.filter(f => f.category === filter);

            return (
                <div className="min-h-screen pb-20">
                    <header className="bg-blue-700 text-white p-4 sticky top-0 z-50 shadow-md">
                        <div className="max-w-md mx-auto flex justify-between items-center">
                            <h1 className="text-lg font-bold">復興支援ポータル</h1>
                            <Icon name="menu" className="w-5 h-5" />
                        </div>
                    </header>

                    <main className="max-w-md mx-auto p-4 space-y-6">
                        {/* カテゴリフィルタ [cite: 334, 508] */}
                        <div className="flex gap-2 overflow-x-auto pb-2 no-scrollbar">
                            {categories.map(c => (
                                <button 
                                    key={c}
                                    onClick={() => setFilter(c)}
                                    className={`px-4 py-1.5 rounded-full text-xs font-bold whitespace-nowrap border transition-all ${
                                        filter === c ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-600 border-slate-200'
                                    }`}
                                >
                                    {c}
                                </button>
                            ))}
                        </div>

                        {/* 施設カードリスト [cite: 512, 819] */}
                        <div className="grid gap-6">
                            {filteredData.map(f => (
                                <div key={f.id} className="bg-white rounded-2xl shadow-sm overflow-hidden border border-slate-100 animate-fade-in">
                                    <div className="relative h-48 bg-slate-200">
                                        <img src={f.images[0]} className="w-full h-full object-cover" />
                                        <div className="absolute top-3 right-3 bg-black/50 text-white text-[10px] px-2 py-1 rounded-full">
                                            1/{f.images.length}
                                        </div>
                                    </div>
                                    <div className="p-5">
                                        <div className="flex justify-between items-start">
                                            <span className="text-[10px] bg-blue-100 text-blue-600 px-2 py-0.5 rounded font-bold">{f.category}</span>
                                            <span className={`text-[10px] font-bold ${f.status === '営業中' ? 'text-emerald-600' : 'text-orange-600'}`}>
                                                ● {f.status}
                                            </span>
                                        </div>
                                        <h2 className="font-bold text-xl mt-2">{f.name}</h2>
                                        <p className="text-sm text-slate-600 mt-2 leading-relaxed">{f.message}</p>
                                        
                                        <div className="mt-4 pt-4 border-t border-slate-50 grid grid-cols-2 gap-3">
                                            <a href={f.ec_url} className="bg-emerald-600 text-white text-center py-2.5 rounded-xl font-bold text-xs shadow-sm active:scale-95 transition-transform">
                                                支援・予約
                                            </a>
                                            <a href={f.map_url} className="bg-white border border-blue-600 text-blue-600 text-center py-2.5 rounded-xl font-bold text-xs active:scale-95 transition-transform">
                                                地図を見る
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </main>
                </div>
            );
        };

        const root = ReactDOM.createRoot(document.getElementById('root'));
        root.render(<App />);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, facilities=facilities)

if __name__ == '__main__':
    # ローカル実行用。Render公開時はポート設定を環境変数から取得します
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
