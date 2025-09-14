import streamlit as st
import ipaddress
import random
import pandas as pd
from typing import List, Tuple
import socket
import struct

# ページ設定
st.set_page_config(
    page_title="IPアドレス",
    page_icon="🌐",
    layout="wide"
)

def binary_to_decimal(binary_str: str) -> int:
    """2進数文字列を10進数に変換"""
    return int(binary_str, 2)

def decimal_to_binary(decimal: int, bits: int = 8) -> str:
    """10進数を指定ビット数の2進数文字列に変換"""
    return format(decimal, f'0{bits}b')

def ip_to_binary(ip: str) -> str:
    """IPv4アドレスを2進数表記に変換"""
    try:
        octets = ip.split('.')
        binary_parts = [decimal_to_binary(int(octet)) for octet in octets]
        return '.'.join(binary_parts)
    except:
        return "無効なIPアドレス"

def cidr_to_subnet_mask(cidr: int) -> str:
    """CIDR記法をサブネットマスクに変換"""
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return socket.inet_ntoa(struct.pack('>I', mask))

def get_network_info(ip: str, cidr: int) -> dict:
    """ネットワーク情報を取得"""
    try:
        network = ipaddress.IPv4Network(f"{ip}/{cidr}", strict=False)
        return {
            'network_address': str(network.network_address),
            'broadcast_address': str(network.broadcast_address),
            'subnet_mask': cidr_to_subnet_mask(cidr),
            'host_count': network.num_addresses - 2,
            'usable_hosts': f"{network.network_address + 1} - {network.broadcast_address - 1}"
        }
    except:
        return None

def analyze_ip_binary(ip: str, cidr: int) -> dict:
    """IPアドレスの2進数分析"""
    try:
        # IPアドレスを32ビットの2進数に変換
        octets = [int(x) for x in ip.split('.')]
        ip_binary = ''.join([format(octet, '08b') for octet in octets])
        
        # サブネットマスクを32ビットの2進数に変換
        mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
        mask_binary = format(mask, '032b')
        
        # ネットワーク部とホスト部を分離
        network_part = ip_binary[:cidr]
        host_part = ip_binary[cidr:]
        
        # ネットワークアドレスとブロードキャストアドレスの2進数
        network_binary = network_part + '0' * (32 - cidr)
        broadcast_binary = network_part + '1' * (32 - cidr)
        
        return {
            'ip_binary': ip_binary,
            'ip_binary_dotted': '.'.join([ip_binary[i:i+8] for i in range(0, 32, 8)]),
            'mask_binary': mask_binary,
            'mask_binary_dotted': '.'.join([mask_binary[i:i+8] for i in range(0, 32, 8)]),
            'network_part': network_part,
            'host_part': host_part,
            'network_binary': network_binary,
            'broadcast_binary': broadcast_binary,
            'network_bits': cidr,
            'host_bits': 32 - cidr
        }
    except:
        return None

def binary_to_ip(binary_str: str) -> str:
    """32ビット2進数文字列をIPアドレスに変換"""
    try:
        # 8ビットずつに分割
        octets = [binary_str[i:i+8] for i in range(0, 32, 8)]
        # 各オクテットを10進数に変換
        decimal_octets = [str(int(octet, 2)) for octet in octets]
        return '.'.join(decimal_octets)
    except:
        return "無効な2進数"

def generate_random_ipv4() -> str:
    """ランダムなIPv4アドレスを生成"""
    return f"{random.randint(1, 254)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def generate_random_ipv6() -> str:
    """ランダムなIPv6アドレスを生成"""
    parts = [format(random.randint(0, 65535), '04x') for _ in range(8)]
    return ':'.join(parts)

def main():
    st.title("IPアドレス（pp.108-111）")
    st.caption("Created by Dit-Lab.(Daiki Ito)")
    st.caption("Supported by Tomoaki ATSUMI")
    st.markdown("IPアドレスとサブネットマスクを体験的に学ぼう！")
    
    # タブでセクション選択
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📚 基本概念", "🔧 IPv4 実践", "🔢 2進数・ホスト部分析", "🔬 IPv6 探索", "🎯 練習問題", "🏠 身近な例"])

    with tab1:
        basic_concepts()
    with tab2:
        ipv4_practice()
    with tab3:
        binary_host_analysis()
    with tab4:
        ipv6_exploration()
    with tab5:
        practice_quiz()
    with tab6:
        real_world_examples()

def basic_concepts():
    st.header("📚 基本概念")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏠 IPアドレスとは？")
        st.markdown("""
        IPアドレスは「インターネット上の住所」です！
        
        **家の住所と比較：**
        - 家の住所：〒123-4567 東京都○○区...
        - IPアドレス：192.168.1.100
        
        **IPv4の特徴：**
        - 4つの数字（0-255）をドットで区切る
        - 例：192.168.1.1
        - 約43億個のアドレス（足りなくなってきた！）
        """)
        
    with col2:
        st.subheader("🌍 IPv6とは？")
        st.markdown("""
        IPv4のアドレス不足を解決する新しいバージョン！
        
        **IPv6の特徴：**
        - 16進数8グループをコロンで区切る
        - 例：2001:0db8:85a3:0000:0000:8a2e:0370:7334
        - 約340澗個のアドレス（ほぼ無限！）
        - より安全で効率的
        """)
    
    # インタラクティブな数値変換デモ
    st.subheader("🔄 数値変換体験")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        decimal_input = st.number_input("10進数を入力（0-255）", 0, 255, 192)
        st.write(f"2進数: **{decimal_to_binary(decimal_input)}**")
        st.write(f"16進数: **{hex(decimal_input).upper()}**")
    
    with col2:
        binary_input = st.text_input("2進数を入力（8桁）", "11000000")
        if len(binary_input) == 8 and all(c in '01' for c in binary_input):
            decimal_result = binary_to_decimal(binary_input)
            st.write(f"10進数: **{decimal_result}**")
            st.write(f"16進数: **{hex(decimal_result).upper()}**")
        else:
            st.error("8桁の2進数を入力してください")
    
    with col3:
        st.markdown("**よく使われる値：**")
        common_values = {
            "0": "00000000",
            "128": "10000000", 
            "192": "11000000",
            "255": "11111111"
        }
        for dec, bin_val in common_values.items():
            st.write(f"{dec} = {bin_val}")

def ipv4_practice():
    st.header("🔧 IPv4 実践体験")
    
    # IPアドレス入力エリア
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 IPアドレス分析")
        ip_input = st.text_input("IPv4アドレスを入力", "192.168.1.100")
        cidr_input = st.slider("CIDR記法（サブネットマスク）", 8, 30, 24)
        
        if st.button("🔍 分析実行"):
            network_info = get_network_info(ip_input, cidr_input)
            if network_info:
                st.success("✅ 分析完了！")
                
                # 結果を表形式で表示
                info_df = pd.DataFrame([
                    ["入力IPアドレス", ip_input],
                    ["CIDR記法", f"/{cidr_input}"],
                    ["サブネットマスク", network_info['subnet_mask']],
                    ["ネットワークアドレス", network_info['network_address']],
                    ["ブロードキャストアドレス", network_info['broadcast_address']],
                    ["利用可能ホスト数", f"{network_info['host_count']:,}台"],
                    ["利用可能範囲", network_info['usable_hosts']]
                ], columns=["項目", "値"])
                
                st.table(info_df)
            else:
                st.error("❌ 無効なIPアドレスです")
    
    with col2:
        st.subheader("🎲 ランダム生成")
        if st.button("ランダムIP生成"):
            random_ip = generate_random_ipv4()
            st.session_state.random_ip = random_ip
        
        if 'random_ip' in st.session_state:
            st.write(f"生成されたIP: **{st.session_state.random_ip}**")
            st.write(f"2進数表記:")
            st.code(ip_to_binary(st.session_state.random_ip))
    
    # ビジュアル説明
    st.subheader("📊 ビジュアル理解")
    
    tab1, tab2, tab3 = st.tabs(["🏢 サブネット分割", "🔢 2進数変換", "📈 CIDR比較"])
    
    with tab1:
        st.markdown("""
        **サブネット分割の例：**
        
        会社のネットワーク 192.168.1.0/24 を部署別に分割する場合：
        """)
        
        subnet_examples = pd.DataFrame([
            ["総務部", "192.168.1.0/26", "192.168.1.1-62", "62台"],
            ["営業部", "192.168.1.64/26", "192.168.1.65-126", "62台"],
            ["開発部", "192.168.1.128/26", "192.168.1.129-190", "62台"],
            ["予備", "192.168.1.192/26", "192.168.1.193-254", "62台"]
        ], columns=["部署", "サブネット", "IPアドレス範囲", "利用可能台数"])
        
        st.table(subnet_examples)
    
    with tab2:
        st.markdown("**IPアドレスの2進数変換：**")
        demo_ip = "192.168.1.100"
        octets = demo_ip.split('.')
        
        binary_demo = pd.DataFrame([
            ["オクテット1", octets[0], decimal_to_binary(int(octets[0]))],
            ["オクテット2", octets[1], decimal_to_binary(int(octets[1]))],
            ["オクテット3", octets[2], decimal_to_binary(int(octets[2]))],
            ["オクテット4", octets[3], decimal_to_binary(int(octets[3]))]
        ], columns=["位置", "10進数", "2進数"])
        
        st.table(binary_demo)
        st.write(f"完全な2進数表記: **{ip_to_binary(demo_ip)}**")
    
    with tab3:
        st.markdown("**CIDR記法による違い：**")
        
        cidr_comparison = pd.DataFrame([
            ["/24", "255.255.255.0", "256台", "小規模オフィス"],
            ["/16", "255.255.0.0", "65,536台", "大企業"],
            ["/8", "255.0.0.0", "16,777,216台", "プロバイダー"]
        ], columns=["CIDR", "サブネットマスク", "アドレス数", "用途例"])
        
        st.table(cidr_comparison)

def binary_host_analysis():
    st.header("🔢 2進数・ホスト部・ネットワーク部分析")
    
    st.markdown("""
    **🎯 このセクションで学ぶこと:**
    - IPアドレスの2進数表記の理解
    - ネットワーク部とホスト部の分割
    - サブネットマスクとAND演算の仕組み
    - ビット計算による実際の計算方法
    """)
    
    # メインの分析エリア
    st.subheader("🔍 詳細分析")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("**IPアドレス設定**")
        ip_input = st.text_input("IPv4アドレス", "192.168.1.100", key="binary_ip")
        cidr_input = st.slider("CIDR (ネットワーク部のビット数)", 8, 30, 24, key="binary_cidr")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🔍 詳細分析実行"):
                binary_info = analyze_ip_binary(ip_input, cidr_input)
                if binary_info:
                    st.session_state.binary_analysis = binary_info
                    st.session_state.analysis_ip = ip_input
                    st.session_state.analysis_cidr = cidr_input
                else:
                    st.error("❌ 無効なIPアドレスです")
        
        with col_btn2:
            if st.button("🎲 ランダム例題生成"):
                random_ip = generate_random_ipv4()
                random_cidr = random.choice([16, 20, 24, 25, 26, 27, 28])
                binary_info = analyze_ip_binary(random_ip, random_cidr)
                if binary_info:
                    st.session_state.binary_analysis = binary_info
                    st.session_state.analysis_ip = random_ip
                    st.session_state.analysis_cidr = random_cidr
    
    with col2:
        st.markdown("**💡 ワンポイント解説**")
        st.info("""
        **ネットワーク部**: 住所の「市区町村」
        **ホスト部**: 住所の「番地」
        
        CIDR /24 = ネットワーク部24ビット
        → ホスト部は8ビット (32-24=8)
        → 2^8 = 256台のアドレス
        """)
    
    # 分析結果の表示
    if 'binary_analysis' in st.session_state:
        st.markdown("---")
        binary_info = st.session_state.binary_analysis
        analysis_ip = st.session_state.analysis_ip
        analysis_cidr = st.session_state.analysis_cidr
        
        st.subheader(f"📊 分析結果: {analysis_ip}/{analysis_cidr}")
        
        # タブで情報を整理
        tab1, tab2, tab3, tab4 = st.tabs(["🔢 2進数変換", "🏠 ネット・ホスト部", "🧮 AND演算", "📋 計算手順"])
        
        with tab1:
            st.markdown("**🔢 2進数表記と構造**")
            
            # 2進数表記テーブル
            binary_table = pd.DataFrame([
                ["IPアドレス (10進)", analysis_ip, "入力されたアドレス"],
                ["IPアドレス (2進)", binary_info['ip_binary_dotted'], "32ビット2進数表記"],
                ["サブネットマスク (10進)", cidr_to_subnet_mask(analysis_cidr), f"/{analysis_cidr}の10進表記"],
                ["サブネットマスク (2進)", binary_info['mask_binary_dotted'], "1がネットワーク部、0がホスト部"],
                ["ネットワーク部", binary_info['network_part'], f"{binary_info['network_bits']}ビット"],
                ["ホスト部", binary_info['host_part'], f"{binary_info['host_bits']}ビット"]
            ], columns=["項目", "値", "説明"])
            
            st.table(binary_table)
            
            # ビジュアル表示
            st.markdown("**🎨 ビジュアル表示**")
            network_visual = "🟦" * binary_info['network_bits'] + "🟨" * binary_info['host_bits']
            st.markdown(f"**ビット構成**: {network_visual}")
            st.markdown("🟦 = ネットワーク部　🟨 = ホスト部")
            
        with tab2:
            st.markdown("**🏠 ネットワーク部・ホスト部の詳細**")
            
            host_info = pd.DataFrame([
                ["ネットワーク部 (2進)", binary_info['network_part'], "同じネットワークを示す部分"],
                ["ホスト部 (2進)", binary_info['host_part'], "個々のデバイスを示す部分"],
                ["ネットワークアドレス", binary_to_ip(binary_info['network_binary']), "ホスト部をすべて0にした値"],
                ["ブロードキャストアドレス", binary_to_ip(binary_info['broadcast_binary']), "ホスト部をすべて1にした値"],
                ["利用可能ホスト数", f"{2**binary_info['host_bits'] - 2:,}台", "全アドレス - ネットワーク - ブロードキャスト"]
            ], columns=["項目", "値", "説明"])
            
            st.table(host_info)
            
            # ホスト部の計算説明
            st.markdown("**🧮 ホスト数の計算**")
            st.markdown(f"""
            - ホスト部のビット数: {binary_info['host_bits']}ビット
            - 理論上のアドレス数: 2^{binary_info['host_bits']} = {2**binary_info['host_bits']:,}個
            - 利用可能ホスト数: {2**binary_info['host_bits']:,} - 2 = {2**binary_info['host_bits'] - 2:,}台
            
            **なぜ-2？**
            - ネットワークアドレス: {binary_to_ip(binary_info['network_binary'])} (通信不可)
            - ブロードキャストアドレス: {binary_to_ip(binary_info['broadcast_binary'])} (全体向け通信)
            """)
        
        with tab3:
            st.markdown("**🧮 AND演算によるネットワーク計算**")
            
            # AND演算の説明
            st.markdown("**IPアドレス AND サブネットマスク = ネットワークアドレス**")
            
            # ビット毎のAND演算表示
            ip_bits = binary_info['ip_binary']
            mask_bits = binary_info['mask_binary']
            result_bits = binary_info['network_binary']
            
            # 8ビットずつに分けて表示
            and_table_data = []
            for i in range(4):
                start_bit = i * 8
                end_bit = (i + 1) * 8
                
                ip_octet = ip_bits[start_bit:end_bit]
                mask_octet = mask_bits[start_bit:end_bit]
                result_octet = result_bits[start_bit:end_bit]
                
                ip_decimal = int(ip_octet, 2)
                mask_decimal = int(mask_octet, 2)
                result_decimal = int(result_octet, 2)
                
                and_table_data.append([
                    f"オクテット{i+1}",
                    f"{ip_decimal} ({ip_octet})",
                    f"{mask_decimal} ({mask_octet})",
                    f"{result_decimal} ({result_octet})"
                ])
            
            and_df = pd.DataFrame(and_table_data, 
                                columns=["位置", "IPアドレス", "サブネットマスク", "結果(AND)"])
            st.table(and_df)
            
            st.markdown("**💡 AND演算のルール:**")
            st.markdown("""
            - 1 AND 1 = 1
            - 1 AND 0 = 0  
            - 0 AND 1 = 0
            - 0 AND 0 = 0
            
            **つまり**: マスクが1の部分だけIPアドレスの値が残る
            """)
        
        with tab4:
            st.markdown("**📋 段階的計算手順**")
            
            step_by_step = f"""
            **Step 1: IPアドレスを2進数に変換**
            ```
            {analysis_ip}
            ↓
            {binary_info['ip_binary_dotted']}
            ```
            
            **Step 2: CIDR記法からサブネットマスクを作成**
            ```
            /{analysis_cidr} → ネットワーク部{analysis_cidr}ビット + ホスト部{binary_info['host_bits']}ビット
            ↓
            {binary_info['mask_binary_dotted']}
            ↓
            {cidr_to_subnet_mask(analysis_cidr)}
            ```
            
            **Step 3: AND演算でネットワークアドレスを求める**
            ```
            IPアドレス:     {binary_info['ip_binary_dotted']}
            サブネットマスク: {binary_info['mask_binary_dotted']}
            ─────────────────────────────────────────
            ネットワーク:   {'.'.join([binary_info['network_binary'][i:i+8] for i in range(0, 32, 8)])}
            ↓
            {binary_to_ip(binary_info['network_binary'])}
            ```
            
            **Step 4: ブロードキャストアドレスを求める**
            ```
            ネットワーク部: {binary_info['network_part']} (変更なし)
            ホスト部:     {'1' * binary_info['host_bits']} (すべて1にする)
            ↓
            {binary_to_ip(binary_info['broadcast_binary'])}
            ```
            
            **Step 5: 利用可能範囲を計算**
            ```
            開始: {binary_to_ip(binary_info['network_binary'])} + 1 = {str(ipaddress.IPv4Address(binary_to_ip(binary_info['network_binary'])) + 1)}
            終了: {binary_to_ip(binary_info['broadcast_binary'])} - 1 = {str(ipaddress.IPv4Address(binary_to_ip(binary_info['broadcast_binary'])) - 1)}
            台数: {2**binary_info['host_bits'] - 2:,}台
            ```
            """
            
            st.markdown(step_by_step)
    
    # インタラクティブ練習エリア
    st.markdown("---")
    st.subheader("🎯 インタラクティブ練習")
    
    practice_col1, practice_col2 = st.columns(2)
    
    with practice_col1:
        st.markdown("**🔢 2進数↔10進数変換練習**")
        
        conversion_type = st.radio("変換方向", ["10進数 → 2進数", "2進数 → 10進数"])
        
        if conversion_type == "10進数 → 2進数":
            decimal_practice = st.number_input("10進数を入力 (0-255)", 0, 255, 192)
            if st.button("変換実行", key="dec_to_bin"):
                result = decimal_to_binary(decimal_practice)
                st.success(f"**{decimal_practice}** → **{result}**")
                
                # 計算過程を表示
                st.markdown("**計算過程:**")
                steps = []
                temp = decimal_practice
                while temp > 0:
                    steps.append(f"{temp} ÷ 2 = {temp//2} あまり {temp%2}")
                    temp //= 2
                
                for step in reversed(steps):
                    st.write(step)
                st.write(f"あまりを下から読む: **{result}**")
        
        else:
            binary_practice = st.text_input("2進数を入力 (8桁)", "11000000")
            if st.button("変換実行", key="bin_to_dec"):
                if len(binary_practice) == 8 and all(c in '01' for c in binary_practice):
                    result = binary_to_decimal(binary_practice)
                    st.success(f"**{binary_practice}** → **{result}**")
                    
                    # 計算過程を表示
                    st.markdown("**計算過程:**")
                    total = 0
                    for i, bit in enumerate(binary_practice):
                        power = 7 - i
                        value = int(bit) * (2 ** power)
                        total += value
                        if int(bit) == 1:
                            st.write(f"位置{i+1}: {bit} × 2^{power} = {value}")
                    st.write(f"合計: **{total}**")
                else:
                    st.error("8桁の2進数を入力してください")
    
    with practice_col2:
        st.markdown("**🏠 ネットワーク計算練習**")
        
        practice_ip = st.text_input("練習用IPアドレス", "172.16.10.50")
        practice_cidr = st.slider("練習用CIDR", 8, 30, 20)
        
        if st.button("練習問題を解く"):
            practice_info = analyze_ip_binary(practice_ip, practice_cidr)
            if practice_info:
                st.markdown("**問題:** 以下を計算してください")
                st.info(f"IPアドレス: {practice_ip}/{practice_cidr}")
                
                with st.expander("💡 答えを見る"):
                    st.write(f"**ネットワークアドレス:** {binary_to_ip(practice_info['network_binary'])}")
                    st.write(f"**ブロードキャストアドレス:** {binary_to_ip(practice_info['broadcast_binary'])}")
                    st.write(f"**利用可能ホスト数:** {2**practice_info['host_bits'] - 2:,}台")
                    st.write(f"**利用可能範囲:** {str(ipaddress.IPv4Address(binary_to_ip(practice_info['network_binary'])) + 1)} - {str(ipaddress.IPv4Address(binary_to_ip(practice_info['broadcast_binary'])) - 1)}")
            else:
                st.error("無効なIPアドレスです")

def ipv6_exploration():
    st.header("🔬 IPv6 探索")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🆚 IPv4 vs IPv6 比較")
        
        comparison_df = pd.DataFrame([
            ["アドレス長", "32ビット", "128ビット"],
            ["表記法", "ドット10進数", "コロン16進数"],
            ["アドレス数", "約43億個", "約340澗個"],
            ["例", "192.168.1.1", "2001:db8::1"],
            ["ヘッダーサイズ", "20-60バイト", "40バイト固定"],
            ["設定方法", "手動/DHCP", "自動設定可能"]
        ], columns=["項目", "IPv4", "IPv6"])
        
        st.table(comparison_df)
    
    with col2:
        st.subheader("🎲 IPv6アドレス生成")
        
        if st.button("ランダムIPv6生成"):
            random_ipv6 = generate_random_ipv6()
            st.session_state.random_ipv6 = random_ipv6
        
        if 'random_ipv6' in st.session_state:
            st.write("生成されたIPv6:")
            st.code(st.session_state.random_ipv6)
            
            # IPv6の短縮表記デモ
            try:
                ipv6_obj = ipaddress.IPv6Address(st.session_state.random_ipv6)
                st.write(f"短縮表記: **{ipv6_obj.compressed}**")
                st.write(f"完全表記: **{ipv6_obj.exploded}**")
            except:
                pass
    
    st.subheader("📐 IPv6の特徴的な仕組み")
    
    tab1, tab2, tab3 = st.tabs(["🏠 アドレス種類", "📝 短縮ルール", "🌐 実際の例"])
    
    with tab1:
        st.markdown("""
        **IPv6のアドレス種類：**
        """)
        
        ipv6_types = pd.DataFrame([
            ["ローカルリンク", "fe80::/10", "同一セグメント内通信"],
            ["ユニーク局所", "fc00::/7", "組織内プライベート"],
            ["グローバル", "2000::/3", "インターネット通信"],
            ["マルチキャスト", "ff00::/8", "一対多通信"],
            ["ループバック", "::1/128", "自分自身"]
        ], columns=["種類", "プレフィックス", "用途"])
        
        st.table(ipv6_types)
    
    with tab2:
        st.markdown("""
        **IPv6短縮ルール：**
        
        1. **先頭の0を省略**: 0001 → 1
        2. **連続する0グループを::で省略** (一度だけ)
        
        **例：**
        """)
        
        shortening_examples = pd.DataFrame([
            ["2001:0db8:0000:0000:0000:0000:0000:0001", "先頭0省略", "2001:db8:0:0:0:0:0:1"],
            ["2001:db8:0:0:0:0:0:1", "連続0省略", "2001:db8::1"],
            ["fe80:0000:0000:0000:0000:0000:0000:0001", "完全短縮", "fe80::1"]
        ], columns=["元のアドレス", "操作", "短縮後"])
        
        st.table(shortening_examples)
    
    with tab3:
        st.markdown("""
        **身近なIPv6アドレス例：**
        """)
        
        real_examples = pd.DataFrame([
            ["Google DNS", "2001:4860:4860::8888", "パブリックDNS"],
            ["Cloudflare DNS", "2606:4700:4700::1111", "パブリックDNS"],
            ["ローカルリンク例", "fe80::1%en0", "ルーター"],
            ["ループバック", "::1", "localhost"]
        ], columns=["サービス", "IPv6アドレス", "説明"])
        
        st.table(real_examples)

def practice_quiz():
    st.header("🎯 練習問題")
    
    if 'quiz_score' not in st.session_state:
        st.session_state.quiz_score = 0
        st.session_state.quiz_total = 0
    
    quiz_type = st.selectbox("問題タイプを選択", 
                           ["🔢 数値変換", "🏠 サブネット計算", "🔢 2進数分析", "🆚 IPv4 vs IPv6"])
    
    if quiz_type == "🔢 数値変換":
        number_conversion_quiz()
    elif quiz_type == "🏠 サブネット計算":
        subnet_calculation_quiz()
    elif quiz_type == "🔢 2進数分析":
        binary_analysis_quiz()
    elif quiz_type == "🆚 IPv4 vs IPv6":
        ipv4_vs_ipv6_quiz()
    
    # スコア表示
    if st.session_state.quiz_total > 0:
        accuracy = (st.session_state.quiz_score / st.session_state.quiz_total) * 100
        st.metric("正答率", f"{accuracy:.1f}%",
                 f"{st.session_state.quiz_score}/{st.session_state.quiz_total}")

def number_conversion_quiz():
    st.subheader("🔢 数値変換クイズ")
    
    if st.button("新しい問題を生成"):
        number = random.randint(1, 255)
        st.session_state.quiz_number = number
        st.session_state.quiz_answered = False
    
    if 'quiz_number' in st.session_state and not st.session_state.get('quiz_answered', False):
        number = st.session_state.quiz_number
        st.write(f"**問題**: {number} を2進数に変換してください")
        
        user_answer = st.text_input("答え（8桁の2進数）", key="binary_answer")
        
        if st.button("回答"):
            correct_answer = decimal_to_binary(number)
            if user_answer == correct_answer:
                st.success(f"🎉 正解！ {number} = {correct_answer}")
                st.session_state.quiz_score += 1
            else:
                st.error(f"❌ 不正解。正解は {correct_answer} です")
            
            st.session_state.quiz_total += 1
            st.session_state.quiz_answered = True

def subnet_calculation_quiz():
    st.subheader("🏠 サブネット計算クイズ")
    
    if st.button("新しい問題を生成", key="subnet_quiz"):
        ip = generate_random_ipv4()
        cidr = random.choice([16, 20, 24, 28])
        st.session_state.quiz_ip = ip
        st.session_state.quiz_cidr = cidr
        st.session_state.subnet_answered = False
    
    if 'quiz_ip' in st.session_state and not st.session_state.get('subnet_answered', False):
        ip = st.session_state.quiz_ip
        cidr = st.session_state.quiz_cidr
        
        st.write(f"**問題**: {ip}/{cidr} のネットワークアドレスは？")
        
        user_answer = st.text_input("ネットワークアドレス", key="network_answer")
        
        if st.button("回答", key="subnet_submit"):
            network_info = get_network_info(ip, cidr)
            correct_answer = network_info['network_address']
            
            if user_answer == correct_answer:
                st.success(f"🎉 正解！ネットワークアドレスは {correct_answer} です")
                st.session_state.quiz_score += 1
            else:
                st.error(f"❌ 不正解。正解は {correct_answer} です")
            
            st.session_state.quiz_total += 1
            st.session_state.subnet_answered = True

def binary_analysis_quiz():
    st.subheader("🔢 2進数分析クイズ")
    
    if st.button("新しい問題を生成", key="binary_quiz"):
        ip = generate_random_ipv4()
        cidr = random.choice([16, 20, 24, 25, 26, 27, 28])
        st.session_state.quiz_binary_ip = ip
        st.session_state.quiz_binary_cidr = cidr
        st.session_state.binary_quiz_answered = False
    
    if 'quiz_binary_ip' in st.session_state and not st.session_state.get('binary_quiz_answered', False):
        ip = st.session_state.quiz_binary_ip
        cidr = st.session_state.quiz_binary_cidr
        
        binary_info = analyze_ip_binary(ip, cidr)
        
        quiz_choice = random.choice([
            "network_bits", "host_bits", "host_count", "network_part"
        ])
        
        if quiz_choice == "network_bits":
            st.write(f"**問題**: {ip}/{cidr} のネットワーク部は何ビット？")
            user_answer = st.number_input("ネットワーク部のビット数", 0, 32, key="network_bits_answer")
            correct_answer = cidr
            
        elif quiz_choice == "host_bits":
            st.write(f"**問題**: {ip}/{cidr} のホスト部は何ビット？")
            user_answer = st.number_input("ホスト部のビット数", 0, 32, key="host_bits_answer")
            correct_answer = 32 - cidr
            
        elif quiz_choice == "host_count":
            st.write(f"**問題**: {ip}/{cidr} で利用可能なホスト数は？")
            user_answer = st.number_input("利用可能ホスト数", 0, 16777214, key="host_count_answer")
            correct_answer = 2 ** (32 - cidr) - 2
            
        elif quiz_choice == "network_part":
            st.write(f"**問題**: {ip} の2進数表記でネットワーク部（最初の{cidr}ビット）は？")
            user_answer = st.text_input("ネットワーク部の2進数", key="network_part_answer")
            correct_answer = binary_info['network_part']
        
        if st.button("回答", key="binary_quiz_submit"):
            if quiz_choice == "network_part":
                is_correct = user_answer == correct_answer
            else:
                is_correct = user_answer == correct_answer
            
            if is_correct:
                st.success(f"🎉 正解！")
                if quiz_choice == "network_bits":
                    st.info(f"CIDR /{cidr} は ネットワーク部が{cidr}ビット を意味します")
                elif quiz_choice == "host_bits":
                    st.info(f"ホスト部 = 32 - {cidr} = {32-cidr}ビット")
                elif quiz_choice == "host_count":
                    st.info(f"2^{32-cidr} - 2 = {2**(32-cidr)} - 2 = {correct_answer:,}台")
                elif quiz_choice == "network_part":
                    st.info(f"IPアドレス {ip} の最初の{cidr}ビット = {correct_answer}")
                
                st.session_state.quiz_score += 1
            else:
                st.error(f"❌ 不正解。正解は {correct_answer} です")
                
                # 詳細解説
                if quiz_choice == "network_bits":
                    st.info("CIDR記法の数字がそのままネットワーク部のビット数です")
                elif quiz_choice == "host_bits":
                    st.info(f"IPv4は32ビット総計なので、ホスト部 = 32 - {cidr} = {32-cidr}ビット")
                elif quiz_choice == "host_count":
                    st.info(f"ホスト部{32-cidr}ビット → 2^{32-cidr} = {2**(32-cidr)}個のアドレス → ネットワーク・ブロードキャスト除いて{correct_answer:,}台")
            
            st.session_state.quiz_total += 1
            st.session_state.binary_quiz_answered = True

def ipv4_vs_ipv6_quiz():
    st.subheader("🆚 IPv4 vs IPv6 クイズ")
    
    questions = [
        {
            "question": "IPv4のアドレス長は何ビット？",
            "options": ["16ビット", "32ビット", "64ビット", "128ビット"],
            "answer": "32ビット"
        },
        {
            "question": "IPv6のアドレス長は何ビット？",
            "options": ["32ビット", "64ビット", "128ビット", "256ビット"],
            "answer": "128ビット"
        },
        {
            "question": "IPv4で使用される区切り文字は？",
            "options": ["ドット(.)", "コロン(:)", "スラッシュ(/)", "ハイフン(-)"],
            "answer": "ドット(.)"
        },
        {
            "question": "IPv6で使用される区切り文字は？",
            "options": ["ドット(.)", "コロン(:)", "セミコロン(;)", "カンマ(,)"],
            "answer": "コロン(:)"
        }
    ]
    
    if st.button("新しい問題を生成", key="ipv6_quiz"):
        question = random.choice(questions)
        st.session_state.current_question = question
        st.session_state.ipv6_answered = False
    
    if 'current_question' in st.session_state and not st.session_state.get('ipv6_answered', False):
        question = st.session_state.current_question
        st.write(f"**問題**: {question['question']}")
        
        user_answer = st.radio("選択してください：", question['options'], key="ipv6_answer")
        
        if st.button("回答", key="ipv6_submit"):
            if user_answer == question['answer']:
                st.success("🎉 正解！")
                st.session_state.quiz_score += 1
            else:
                st.error(f"❌ 不正解。正解は「{question['answer']}」です")
            
            st.session_state.quiz_total += 1
            st.session_state.ipv6_answered = True

def real_world_examples():
    st.header("🏠 身近な例で理解")
    
    tab1, tab2, tab3 = st.tabs(["🏫 学校ネットワーク", "🏠 家庭ネットワーク", "🌐 インターネット"])
    
    with tab1:
        st.subheader("🏫 学校のネットワーク例")
        st.markdown("""
        **大規模高校のネットワーク設計例：**
        
        全体ネットワーク: **10.1.0.0/16** (65,534台)
        """)
        
        school_network = pd.DataFrame([
            ["職員室", "10.1.1.0/24", "254台", "先生のPC・プリンタ"],
            ["PC教室A", "10.1.10.0/25", "126台", "授業用PC"],
            ["PC教室B", "10.1.10.128/25", "126台", "授業用PC"],
            ["図書館", "10.1.20.0/26", "62台", "検索端末・PC"],
            ["無線LAN", "10.1.100.0/22", "1,022台", "生徒・教員のスマホ・タブレット"],
            ["サーバー", "10.1.200.0/28", "14台", "校務システム・ファイルサーバー"]
        ], columns=["エリア", "サブネット", "最大台数", "用途"])
        
        st.table(school_network)
        
        st.info("💡 ポイント: 用途に応じてサブネットを分けることで、セキュリティと管理が向上します！")
    
    with tab2:
        st.subheader("🏠 家庭のネットワーク例")
        st.markdown("""
        **一般的な家庭ネットワーク: 192.168.1.0/24**
        """)
        
        home_devices = pd.DataFrame([
            ["ルーター", "192.168.1.1", "ゲートウェイ"],
            ["お父さんのPC", "192.168.1.10", "固定IP"],
            ["お母さんのノートPC", "192.168.1.11", "固定IP"],
            ["あなたのスマホ", "192.168.1.20", "DHCP自動割当"],
            ["テレビ", "192.168.1.30", "Netflix・YouTube視聴"],
            ["ゲーム機", "192.168.1.40", "オンラインゲーム"],
            ["プリンター", "192.168.1.50", "共有プリンター"],
            ["スマートスピーカー", "192.168.1.60", "IoTデバイス"]
        ], columns=["デバイス", "IPアドレス", "説明"])
        
        st.table(home_devices)
        
        st.warning("🔒 セキュリティTips: 家庭ネットワークでも不要なポートは閉じ、強力なWi-Fiパスワードを設定しましょう！")
    
    with tab3:
        st.subheader("🌐 インターネットの仕組み")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **パブリックIPアドレス例：**
            
            **Webサイト:**
            - Google: 8.8.8.8
            - YouTube: 142.250.196.78
            - Twitter: 104.244.42.1
            
            **DNS サーバー:**
            - Google DNS: 8.8.8.8
            - Cloudflare: 1.1.1.1
            """)
        
        with col2:
            st.markdown("""
            **プライベートIPアドレス範囲：**
            
            - **Class A**: 10.0.0.0 ～ 10.255.255.255
            - **Class B**: 172.16.0.0 ～ 172.31.255.255  
            - **Class C**: 192.168.0.0 ～ 192.168.255.255
            
            これらは家庭・企業内でのみ使用され、
            インターネット上には存在しません。
            """)
        
        st.markdown("""
        **🌍 IPv6の未来:**
        
        - **現在**: IPv4とIPv6が併存（デュアルスタック）
        - **近い将来**: IPv6が主流になる予定
        - **メリット**: アドレス不足解消、セキュリティ向上、設定簡素化
        """)
        
        st.success("🎓 おめでとうございます！これでIPアドレスとサブネットの基本をマスターしました！")

if __name__ == "__main__":
    main()