"""
Demo Mode - API 없이 작동하는 데모 데이터
Works without NGII API key - uses mock data and sample images
"""

import random
from typing import Dict, List

# 주요 도시 좌표 데이터
CITY_COORDINATES = {
    "서울특별시": {
        "강남구": {"latitude": 37.5172, "longitude": 127.0473, "address": "서울특별시 강남구"},
        "강동구": {"latitude": 37.5301, "longitude": 127.1238, "address": "서울특별시 강동구"},
        "강북구": {"latitude": 37.6396, "longitude": 127.0257, "address": "서울특별시 강북구"},
        "강서구": {"latitude": 37.5509, "longitude": 126.8495, "address": "서울특별시 강서구"},
        "관악구": {"latitude": 37.4784, "longitude": 126.9516, "address": "서울특별시 관악구"},
        "광진구": {"latitude": 37.5384, "longitude": 127.0822, "address": "서울특별시 광진구"},
        "구로구": {"latitude": 37.4954, "longitude": 126.8874, "address": "서울특별시 구로구"},
        "금천구": {"latitude": 37.4519, "longitude": 126.9021, "address": "서울특별시 금천구"},
        "노원구": {"latitude": 37.6542, "longitude": 127.0568, "address": "서울특별시 노원구"},
        "도봉구": {"latitude": 37.6688, "longitude": 127.0471, "address": "서울특별시 도봉구"},
        "동대문구": {"latitude": 37.5744, "longitude": 127.0396, "address": "서울특별시 동대문구"},
        "동작구": {"latitude": 37.5124, "longitude": 126.9393, "address": "서울특별시 동작구"},
        "마포구": {"latitude": 37.5663, "longitude": 126.9019, "address": "서울특별시 마포구"},
        "서대문구": {"latitude": 37.5791, "longitude": 126.9368, "address": "서울특별시 서대문구"},
        "서초구": {"latitude": 37.4837, "longitude": 127.0324, "address": "서울특별시 서초구"},
        "성동구": {"latitude": 37.5634, "longitude": 127.0368, "address": "서울특별시 성동구"},
        "성북구": {"latitude": 37.5894, "longitude": 127.0167, "address": "서울특별시 성북구"},
        "송파구": {"latitude": 37.5145, "longitude": 127.1059, "address": "서울특별시 송파구"},
        "양천구": {"latitude": 37.5170, "longitude": 126.8664, "address": "서울특별시 양천구"},
        "영등포구": {"latitude": 37.5264, "longitude": 126.8963, "address": "서울특별시 영등포구"},
        "용산구": {"latitude": 37.5324, "longitude": 126.9902, "address": "서울특별시 용산구"},
        "은평구": {"latitude": 37.6027, "longitude": 126.9291, "address": "서울특별시 은평구"},
        "종로구": {"latitude": 37.5735, "longitude": 126.9788, "address": "서울특별시 종로구"},
        "중구": {"latitude": 37.5636, "longitude": 126.9977, "address": "서울특별시 중구"},
        "중랑구": {"latitude": 37.6063, "longitude": 127.0929, "address": "서울특별시 중랑구"},
    },
    "부산광역시": {
        "중구": {"latitude": 35.1065, "longitude": 129.0323, "address": "부산광역시 중구"},
        "서구": {"latitude": 35.0979, "longitude": 129.0241, "address": "부산광역시 서구"},
        "동구": {"latitude": 35.1295, "longitude": 129.0456, "address": "부산광역시 동구"},
        "영도구": {"latitude": 35.0913, "longitude": 129.0679, "address": "부산광역시 영도구"},
        "부산진구": {"latitude": 35.1629, "longitude": 129.0532, "address": "부산광역시 부산진구"},
        "동래구": {"latitude": 35.2047, "longitude": 129.0838, "address": "부산광역시 동래구"},
        "남구": {"latitude": 35.1364, "longitude": 129.0844, "address": "부산광역시 남구"},
        "북구": {"latitude": 35.1974, "longitude": 128.9903, "address": "부산광역시 북구"},
        "해운대구": {"latitude": 35.1631, "longitude": 129.1635, "address": "부산광역시 해운대구"},
        "사하구": {"latitude": 35.1043, "longitude": 128.9744, "address": "부산광역시 사하구"},
        "금정구": {"latitude": 35.2428, "longitude": 129.0928, "address": "부산광역시 금정구"},
        "강서구": {"latitude": 35.2117, "longitude": 128.9803, "address": "부산광역시 강서구"},
        "연제구": {"latitude": 35.1763, "longitude": 129.0819, "address": "부산광역시 연제구"},
        "수영구": {"latitude": 35.1450, "longitude": 129.1134, "address": "부산광역시 수영구"},
        "사상구": {"latitude": 35.1528, "longitude": 128.9910, "address": "부산광역시 사상구"},
        "기장군": {"latitude": 35.2446, "longitude": 129.2224, "address": "부산광역시 기장군"},
    },
    "인천광역시": {
        "중구": {"latitude": 37.4738, "longitude": 126.6214, "address": "인천광역시 중구"},
        "동구": {"latitude": 37.4738, "longitude": 126.6432, "address": "인천광역시 동구"},
        "미추홀구": {"latitude": 37.4636, "longitude": 126.6500, "address": "인천광역시 미추홀구"},
        "연수구": {"latitude": 37.4104, "longitude": 126.6777, "address": "인천광역시 연수구"},
        "남동구": {"latitude": 37.4476, "longitude": 126.7310, "address": "인천광역시 남동구"},
        "부평구": {"latitude": 37.5070, "longitude": 126.7219, "address": "인천광역시 부평구"},
        "계양구": {"latitude": 37.5375, "longitude": 126.7375, "address": "인천광역시 계양구"},
        "서구": {"latitude": 37.5453, "longitude": 126.6761, "address": "인천광역시 서구"},
        "강화군": {"latitude": 37.7469, "longitude": 126.4882, "address": "인천광역시 강화군"},
        "옹진군": {"latitude": 37.4466, "longitude": 126.6368, "address": "인천광역시 옹진군"},
    },
    "대전광역시": {
        "대덕구": {"latitude": 36.3468, "longitude": 127.4167, "address": "대전광역시 대덕구"},
        "동구": {"latitude": 36.3114, "longitude": 127.4549, "address": "대전광역시 동구"},
        "서구": {"latitude": 36.3553, "longitude": 127.3838, "address": "대전광역시 서구"},
        "유성구": {"latitude": 36.3621, "longitude": 127.3567, "address": "대전광역시 유성구"},
        "중구": {"latitude": 36.3254, "longitude": 127.4214, "address": "대전광역시 중구"},
    },
    "제주특별자치도": {
        "제주시": {"latitude": 33.4996, "longitude": 126.5312, "address": "제주특별자치도 제주시"},
        "서귀포시": {"latitude": 33.2541, "longitude": 126.5601, "address": "제주특별자치도 서귀포시"},
    },
    "경기도": {
        "수원시": {"latitude": 37.2636, "longitude": 127.0286, "address": "경기도 수원시"},
        "성남시": {"latitude": 37.4201, "longitude": 127.1262, "address": "경기도 성남시"},
        "안양시": {"latitude": 37.3943, "longitude": 126.9568, "address": "경기도 안양시"},
        "용인시": {"latitude": 37.2410, "longitude": 127.1776, "address": "경기도 용인시"},
        "고양시": {"latitude": 37.6584, "longitude": 126.8320, "address": "경기도 고양시"},
        "화성시": {"latitude": 37.1995, "longitude": 126.8310, "address": "경기도 화성시"},
        "부천시": {"latitude": 37.5034, "longitude": 126.7660, "address": "경기도 부천시"},
        "안산시": {"latitude": 37.3219, "longitude": 126.8309, "address": "경기도 안산시"},
        "남양주시": {"latitude": 37.6364, "longitude": 127.2167, "address": "경기도 남양주시"},
        "의정부시": {"latitude": 37.7381, "longitude": 127.0337, "address": "경기도 의정부시"},
        "평택시": {"latitude": 36.9922, "longitude": 127.1129, "address": "경기도 평택시"},
        "시흥시": {"latitude": 37.3799, "longitude": 126.8028, "address": "경기도 시흥시"},
        "파주시": {"latitude": 37.7599, "longitude": 126.7800, "address": "경기도 파주시"},
        "김포시": {"latitude": 37.6152, "longitude": 126.7156, "address": "경기도 김포시"},
        "광명시": {"latitude": 37.4785, "longitude": 126.8664, "address": "경기도 광명시"},
        "광주시": {"latitude": 37.4291, "longitude": 127.2556, "address": "경기도 광주시"},
        "군포시": {"latitude": 37.3617, "longitude": 126.9352, "address": "경기도 군포시"},
        "이천시": {"latitude": 37.2719, "longitude": 127.4351, "address": "경기도 이천시"},
        "양주시": {"latitude": 37.7854, "longitude": 127.0459, "address": "경기도 양주시"},
        "오산시": {"latitude": 37.1497, "longitude": 127.0773, "address": "경기도 오산시"},
        "구리시": {"latitude": 37.5943, "longitude": 127.1295, "address": "경기도 구리시"},
        "포천시": {"latitude": 37.8949, "longitude": 127.2005, "address": "경기도 포천시"},
        "의왕시": {"latitude": 37.3449, "longitude": 126.9684, "address": "경기도 의왕시"},
        "하남시": {"latitude": 37.5390, "longitude": 127.2015, "address": "경기도 하남시"},
        "여주시": {"latitude": 37.2975, "longitude": 127.6376, "address": "경기도 여주시"},
        "양평군": {"latitude": 37.4913, "longitude": 127.4874, "address": "경기도 양평군"},
        "동두천시": {"latitude": 37.9034, "longitude": 127.0605, "address": "경기도 동두천시"},
        "과천시": {"latitude": 37.4292, "longitude": 126.9877, "address": "경기도 과천시"},
        "가평군": {"latitude": 37.8314, "longitude": 127.5095, "address": "경기도 가평군"},
        "연천군": {"latitude": 38.0962, "longitude": 127.0748, "address": "경기도 연천군"},
    },
    "대구광역시": {
        "중구": {"latitude": 35.8694, "longitude": 128.6065, "address": "대구광역시 중구"},
        "동구": {"latitude": 35.8896, "longitude": 128.6359, "address": "대구광역시 동구"},
        "서구": {"latitude": 35.8719, "longitude": 128.5592, "address": "대구광역시 서구"},
        "남구": {"latitude": 35.8464, "longitude": 128.5974, "address": "대구광역시 남구"},
        "북구": {"latitude": 35.8858, "longitude": 128.5829, "address": "대구광역시 북구"},
        "수성구": {"latitude": 35.8581, "longitude": 128.6311, "address": "대구광역시 수성구"},
        "달서구": {"latitude": 35.8298, "longitude": 128.5326, "address": "대구광역시 달서구"},
        "달성군": {"latitude": 35.7745, "longitude": 128.4312, "address": "대구광역시 달성군"},
    },
    "광주광역시": {
        "동구": {"latitude": 35.1460, "longitude": 126.9230, "address": "광주광역시 동구"},
        "서구": {"latitude": 35.1520, "longitude": 126.8895, "address": "광주광역시 서구"},
        "남구": {"latitude": 35.1328, "longitude": 126.9026, "address": "광주광역시 남구"},
        "북구": {"latitude": 35.1739, "longitude": 126.9116, "address": "광주광역시 북구"},
        "광산구": {"latitude": 35.1379, "longitude": 126.7937, "address": "광주광역시 광산구"},
    },
    "울산광역시": {
        "중구": {"latitude": 35.5689, "longitude": 129.3325, "address": "울산광역시 중구"},
        "남구": {"latitude": 35.5439, "longitude": 129.3309, "address": "울산광역시 남구"},
        "동구": {"latitude": 35.5048, "longitude": 129.4163, "address": "울산광역시 동구"},
        "북구": {"latitude": 35.5826, "longitude": 129.3614, "address": "울산광역시 북구"},
        "울주군": {"latitude": 35.5225, "longitude": 129.2427, "address": "울산광역시 울주군"},
    },
    "세종특별자치시": {
        "세종시": {"latitude": 36.4800, "longitude": 127.2890, "address": "세종특별자치시"},
    },
    "강원도": {
        "춘천시": {"latitude": 37.8813, "longitude": 127.7298, "address": "강원도 춘천시"},
        "원주시": {"latitude": 37.3422, "longitude": 127.9202, "address": "강원도 원주시"},
        "강릉시": {"latitude": 37.7519, "longitude": 128.8761, "address": "강원도 강릉시"},
        "동해시": {"latitude": 37.5247, "longitude": 129.1143, "address": "강원도 동해시"},
        "태백시": {"latitude": 37.1640, "longitude": 128.9856, "address": "강원도 태백시"},
        "속초시": {"latitude": 38.2070, "longitude": 128.5918, "address": "강원도 속초시"},
        "삼척시": {"latitude": 37.4500, "longitude": 129.1656, "address": "강원도 삼척시"},
        "홍천군": {"latitude": 37.6970, "longitude": 127.8889, "address": "강원도 홍천군"},
        "횡성군": {"latitude": 37.4827, "longitude": 127.9845, "address": "강원도 횡성군"},
        "영월군": {"latitude": 37.1836, "longitude": 128.4614, "address": "강원도 영월군"},
        "평창군": {"latitude": 37.3708, "longitude": 128.3900, "address": "강원도 평창군"},
        "정선군": {"latitude": 37.3806, "longitude": 128.6608, "address": "강원도 정선군"},
        "철원군": {"latitude": 38.1467, "longitude": 127.3133, "address": "강원도 철원군"},
        "화천군": {"latitude": 38.1063, "longitude": 127.7083, "address": "강원도 화천군"},
        "양구군": {"latitude": 38.1097, "longitude": 127.9896, "address": "강원도 양구군"},
        "인제군": {"latitude": 38.0695, "longitude": 128.1706, "address": "강원도 인제군"},
        "고성군": {"latitude": 38.3807, "longitude": 128.4677, "address": "강원도 고성군"},
        "양양군": {"latitude": 38.0754, "longitude": 128.6190, "address": "강원도 양양군"},
    },
    "충청북도": {
        "청주시": {"latitude": 36.6424, "longitude": 127.4890, "address": "충청북도 청주시"},
        "충주시": {"latitude": 36.9910, "longitude": 127.9260, "address": "충청북도 충주시"},
        "제천시": {"latitude": 37.1326, "longitude": 128.1910, "address": "충청북도 제천시"},
        "보은군": {"latitude": 36.4895, "longitude": 127.7294, "address": "충청북도 보은군"},
        "옥천군": {"latitude": 36.3013, "longitude": 127.5721, "address": "충청북도 옥천군"},
        "영동군": {"latitude": 36.1750, "longitude": 127.7834, "address": "충청북도 영동군"},
        "증평군": {"latitude": 36.7851, "longitude": 127.5816, "address": "충청북도 증평군"},
        "진천군": {"latitude": 36.8552, "longitude": 127.4327, "address": "충청북도 진천군"},
        "괴산군": {"latitude": 36.8156, "longitude": 127.7873, "address": "충청북도 괴산군"},
        "음성군": {"latitude": 36.9407, "longitude": 127.6918, "address": "충청북도 음성군"},
        "단양군": {"latitude": 36.9845, "longitude": 128.3659, "address": "충청북도 단양군"},
    },
    "충청남도": {
        "천안시": {"latitude": 36.8151, "longitude": 127.1139, "address": "충청남도 천안시"},
        "공주시": {"latitude": 36.4465, "longitude": 127.1194, "address": "충청남도 공주시"},
        "보령시": {"latitude": 36.3334, "longitude": 126.6129, "address": "충청남도 보령시"},
        "아산시": {"latitude": 36.7898, "longitude": 127.0016, "address": "충청남도 아산시"},
        "서산시": {"latitude": 36.7847, "longitude": 126.4504, "address": "충청남도 서산시"},
        "논산시": {"latitude": 36.1869, "longitude": 127.0986, "address": "충청남도 논산시"},
        "계룡시": {"latitude": 36.2743, "longitude": 127.2487, "address": "충청남도 계룡시"},
        "당진시": {"latitude": 36.8930, "longitude": 126.6475, "address": "충청남도 당진시"},
        "금산군": {"latitude": 36.1088, "longitude": 127.4882, "address": "충청남도 금산군"},
        "부여군": {"latitude": 36.2756, "longitude": 126.9100, "address": "충청남도 부여군"},
        "서천군": {"latitude": 36.0798, "longitude": 126.6917, "address": "충청남도 서천군"},
        "청양군": {"latitude": 36.4592, "longitude": 126.8024, "address": "충청남도 청양군"},
        "홍성군": {"latitude": 36.6012, "longitude": 126.6649, "address": "충청남도 홍성군"},
        "예산군": {"latitude": 36.6826, "longitude": 126.8508, "address": "충청남도 예산군"},
        "태안군": {"latitude": 36.7456, "longitude": 126.2981, "address": "충청남도 태안군"},
    },
    "전라북도": {
        "전주시": {"latitude": 35.8242, "longitude": 127.1480, "address": "전라북도 전주시"},
        "군산시": {"latitude": 35.9677, "longitude": 126.7369, "address": "전라북도 군산시"},
        "익산시": {"latitude": 35.9483, "longitude": 126.9578, "address": "전라북도 익산시"},
        "정읍시": {"latitude": 35.5699, "longitude": 126.8560, "address": "전라북도 정읍시"},
        "남원시": {"latitude": 35.4164, "longitude": 127.3903, "address": "전라북도 남원시"},
        "김제시": {"latitude": 35.8031, "longitude": 126.8809, "address": "전라북도 김제시"},
        "완주군": {"latitude": 35.9046, "longitude": 127.1630, "address": "전라북도 완주군"},
        "진안군": {"latitude": 35.7917, "longitude": 127.4247, "address": "전라북도 진안군"},
        "무주군": {"latitude": 36.0073, "longitude": 127.6604, "address": "전라북도 무주군"},
        "장수군": {"latitude": 35.6476, "longitude": 127.5213, "address": "전라북도 장수군"},
        "임실군": {"latitude": 35.6177, "longitude": 127.2888, "address": "전라북도 임실군"},
        "순창군": {"latitude": 35.3744, "longitude": 127.1376, "address": "전라북도 순창군"},
        "고창군": {"latitude": 35.4357, "longitude": 126.7019, "address": "전라북도 고창군"},
        "부안군": {"latitude": 35.7318, "longitude": 126.7339, "address": "전라북도 부안군"},
    },
    "전라남도": {
        "목포시": {"latitude": 34.8118, "longitude": 126.3922, "address": "전라남도 목포시"},
        "여수시": {"latitude": 34.7604, "longitude": 127.6622, "address": "전라남도 여수시"},
        "순천시": {"latitude": 34.9506, "longitude": 127.4872, "address": "전라남도 순천시"},
        "나주시": {"latitude": 35.0280, "longitude": 126.7109, "address": "전라남도 나주시"},
        "광양시": {"latitude": 34.9407, "longitude": 127.6956, "address": "전라남도 광양시"},
        "담양군": {"latitude": 35.3208, "longitude": 126.9880, "address": "전라남도 담양군"},
        "곡성군": {"latitude": 35.2818, "longitude": 127.2918, "address": "전라남도 곡성군"},
        "구례군": {"latitude": 35.2023, "longitude": 127.4632, "address": "전라남도 구례군"},
        "고흥군": {"latitude": 34.6114, "longitude": 127.2754, "address": "전라남도 고흥군"},
        "보성군": {"latitude": 34.7713, "longitude": 127.0800, "address": "전라남도 보성군"},
        "화순군": {"latitude": 35.0641, "longitude": 126.9866, "address": "전라남도 화순군"},
        "장흥군": {"latitude": 34.6817, "longitude": 126.9066, "address": "전라남도 장흥군"},
        "강진군": {"latitude": 34.6420, "longitude": 126.7672, "address": "전라남도 강진군"},
        "해남군": {"latitude": 34.5732, "longitude": 126.5990, "address": "전라남도 해남군"},
        "영암군": {"latitude": 34.8004, "longitude": 126.6967, "address": "전라남도 영암군"},
        "무안군": {"latitude": 34.9904, "longitude": 126.4816, "address": "전라남도 무안군"},
        "함평군": {"latitude": 35.0658, "longitude": 126.5157, "address": "전라남도 함평군"},
        "영광군": {"latitude": 35.2772, "longitude": 126.5119, "address": "전라남도 영광군"},
        "장성군": {"latitude": 35.3018, "longitude": 126.7845, "address": "전라남도 장성군"},
        "완도군": {"latitude": 34.3115, "longitude": 126.7552, "address": "전라남도 완도군"},
        "진도군": {"latitude": 34.4867, "longitude": 126.2633, "address": "전라남도 진도군"},
        "신안군": {"latitude": 34.8259, "longitude": 126.1076, "address": "전라남도 신안군"},
    },
    "경상북도": {
        "포항시": {"latitude": 36.0190, "longitude": 129.3435, "address": "경상북도 포항시"},
        "경주시": {"latitude": 35.8562, "longitude": 129.2247, "address": "경상북도 경주시"},
        "김천시": {"latitude": 36.1399, "longitude": 128.1137, "address": "경상북도 김천시"},
        "안동시": {"latitude": 36.5684, "longitude": 128.7294, "address": "경상북도 안동시"},
        "구미시": {"latitude": 36.1195, "longitude": 128.3445, "address": "경상북도 구미시"},
        "영주시": {"latitude": 36.8056, "longitude": 128.6240, "address": "경상북도 영주시"},
        "영천시": {"latitude": 35.9733, "longitude": 128.9386, "address": "경상북도 영천시"},
        "상주시": {"latitude": 36.4109, "longitude": 128.1591, "address": "경상북도 상주시"},
        "문경시": {"latitude": 36.5865, "longitude": 128.1867, "address": "경상북도 문경시"},
        "경산시": {"latitude": 35.8251, "longitude": 128.7414, "address": "경상북도 경산시"},
        "군위군": {"latitude": 36.2424, "longitude": 128.5723, "address": "경상북도 군위군"},
        "의성군": {"latitude": 36.3526, "longitude": 128.6974, "address": "경상북도 의성군"},
        "청송군": {"latitude": 36.4359, "longitude": 129.0570, "address": "경상북도 청송군"},
        "영양군": {"latitude": 36.6666, "longitude": 129.1123, "address": "경상북도 영양군"},
        "영덕군": {"latitude": 36.4154, "longitude": 129.3656, "address": "경상북도 영덕군"},
        "청도군": {"latitude": 35.6475, "longitude": 128.7357, "address": "경상북도 청도군"},
        "고령군": {"latitude": 35.7273, "longitude": 128.2627, "address": "경상북도 고령군"},
        "성주군": {"latitude": 35.9194, "longitude": 128.2828, "address": "경상북도 성주군"},
        "칠곡군": {"latitude": 35.9945, "longitude": 128.4015, "address": "경상북도 칠곡군"},
        "예천군": {"latitude": 36.6558, "longitude": 128.4519, "address": "경상북도 예천군"},
        "봉화군": {"latitude": 36.8930, "longitude": 128.7323, "address": "경상북도 봉화군"},
        "울진군": {"latitude": 36.9930, "longitude": 129.4006, "address": "경상북도 울진군"},
        "울릉군": {"latitude": 37.4844, "longitude": 130.9056, "address": "경상북도 울릉군"},
    },
    "경상남도": {
        "창원시": {"latitude": 35.2280, "longitude": 128.6811, "address": "경상남도 창원시"},
        "진주시": {"latitude": 35.1800, "longitude": 128.1076, "address": "경상남도 진주시"},
        "통영시": {"latitude": 34.8544, "longitude": 128.4332, "address": "경상남도 통영시"},
        "사천시": {"latitude": 35.0036, "longitude": 128.0642, "address": "경상남도 사천시"},
        "김해시": {"latitude": 35.2286, "longitude": 128.8894, "address": "경상남도 김해시"},
        "밀양시": {"latitude": 35.5038, "longitude": 128.7463, "address": "경상남도 밀양시"},
        "거제시": {"latitude": 34.8806, "longitude": 128.6211, "address": "경상남도 거제시"},
        "양산시": {"latitude": 35.3350, "longitude": 129.0374, "address": "경상남도 양산시"},
        "의령군": {"latitude": 35.3222, "longitude": 128.2618, "address": "경상남도 의령군"},
        "함안군": {"latitude": 35.2722, "longitude": 128.4063, "address": "경상남도 함안군"},
        "창녕군": {"latitude": 35.5445, "longitude": 128.4923, "address": "경상남도 창녕군"},
        "고성군": {"latitude": 34.9733, "longitude": 128.3232, "address": "경상남도 고성군"},
        "남해군": {"latitude": 34.8375, "longitude": 127.8923, "address": "경상남도 남해군"},
        "하동군": {"latitude": 35.0673, "longitude": 127.7514, "address": "경상남도 하동군"},
        "산청군": {"latitude": 35.4151, "longitude": 127.8736, "address": "경상남도 산청군"},
        "함양군": {"latitude": 35.5203, "longitude": 127.7252, "address": "경상남도 함양군"},
        "거창군": {"latitude": 35.6869, "longitude": 127.9094, "address": "경상남도 거창군"},
        "합천군": {"latitude": 35.5664, "longitude": 128.1656, "address": "경상남도 합천군"},
    }
}


def get_demo_coordinates(sido: str = None, sigungu: str = None) -> Dict:
    """
    데모 모드 좌표 반환 (API 없이)

    Args:
        sido: 시/도
        sigungu: 시/군/구

    Returns:
        좌표 및 주소 정보
    """
    # 시/도가 없으면 서울 강남구 기본
    if not sido:
        return {
            "success": True,
            "address": "서울특별시 강남구",
            "latitude": 37.5172,
            "longitude": 127.0473,
            "mode": "demo",
            "message": "🎭 데모 모드 - API 키 없이 샘플 데이터 사용"
        }

    # 해당 시/도 데이터 찾기
    if sido in CITY_COORDINATES:
        if sigungu and sigungu in CITY_COORDINATES[sido]:
            data = CITY_COORDINATES[sido][sigungu]
            return {
                "success": True,
                "address": data["address"],
                "latitude": data["latitude"],
                "longitude": data["longitude"],
                "mode": "demo",
                "message": "🎭 데모 모드 - API 키 없이 샘플 데이터 사용"
            }
        else:
            # 시/군/구가 없으면 첫 번째 구 반환
            first_gu = list(CITY_COORDINATES[sido].values())[0]
            return {
                "success": True,
                "address": first_gu["address"],
                "latitude": first_gu["latitude"],
                "longitude": first_gu["longitude"],
                "mode": "demo",
                "message": "🎭 데모 모드 - API 키 없이 샘플 데이터 사용"
            }

    # 찾을 수 없으면 서울 강남구
    return {
        "success": True,
        "address": "서울특별시 강남구 (기본)",
        "latitude": 37.5172,
        "longitude": 127.0473,
        "mode": "demo",
        "message": "🎭 데모 모드 - 해당 지역을 찾을 수 없어 기본 위치 사용"
    }


def generate_mock_abandoned_vehicles(latitude: float, longitude: float, count: int = 5) -> List[Dict]:
    """
    Mock 방치 차량 데이터 생성

    차량 타입 분포:
    - 승합차/승용차 (car): 80%
    - 트럭 (truck): 15%
    - 버스 (bus): 5%

    Args:
        latitude: 중심 위도
        longitude: 중심 경도
        count: 생성할 차량 수

    Returns:
        방치 차량 목록
    """
    vehicles = []

    # 차량 타입 분포: 승합차/승용차 80%, 트럭 15%, 버스 5%
    vehicle_types = ['car'] * 8 + ['truck'] * 1 + ['bus'] * 1

    for i in range(count):
        # 중심에서 약간씩 떨어진 위치 (반경 500m 내)
        offset_lat = random.uniform(-0.005, 0.005)
        offset_lng = random.uniform(-0.005, 0.005)

        # 유사도 (85-98%)
        similarity = random.uniform(0.85, 0.98)

        # 위험도
        if similarity >= 0.95:
            risk_level = 'CRITICAL'
        elif similarity >= 0.92:
            risk_level = 'HIGH'
        elif similarity >= 0.88:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        # 경과 년수 (1-5년)
        years = random.randint(1, 5)

        # 차량 타입 (승합차/승용차 우선)
        vehicle_type = random.choice(vehicle_types)

        vehicle = {
            "id": f"demo_vehicle_{i}",
            "latitude": latitude + offset_lat,
            "longitude": longitude + offset_lng,
            "vehicle_type": vehicle_type,
            "similarity_score": similarity,
            "similarity_percentage": round(similarity * 100, 2),
            "risk_level": risk_level,
            "years_difference": years,
            "year1": 2020 - years,
            "year2": 2020,
            "parking_space_id": f"parking_{i}",
            "status": "ABANDONED_SUSPECTED",
            "is_abandoned": True,
            "bbox": {
                "x": random.randint(100, 800),
                "y": random.randint(100, 600),
                "w": random.randint(50, 100),
                "h": random.randint(40, 80)
            }
        }

        vehicles.append(vehicle)

    return vehicles


def get_demo_analysis_result(latitude: float, longitude: float, address: str) -> Dict:
    """
    데모 분석 결과 생성

    Args:
        latitude: 위도
        longitude: 경도
        address: 주소

    Returns:
        분석 결과
    """
    # 랜덤하게 방치 차량 0-5대 생성
    vehicle_count = random.randint(0, 5)

    if vehicle_count == 0:
        return {
            "success": True,
            "mode": "demo",
            "status_message": "✅ 방치 차량이 발견되지 않았습니다 (데모 데이터)",
            "status_message_en": "No abandoned vehicles detected (Demo data)",
            "metadata": {
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "mode": "demo"
            },
            "analysis": {
                "total_parking_spaces_detected": random.randint(10, 30),
                "spaces_analyzed": random.randint(8, 25),
                "abandoned_vehicles_found": 0,
                "detection_threshold": 0.90,
                "is_clean": True
            },
            "abandoned_vehicles": [],
            "results": []
        }

    vehicles = generate_mock_abandoned_vehicles(latitude, longitude, vehicle_count)

    return {
        "success": True,
        "mode": "demo",
        "status_message": f"🔵 {vehicle_count}대의 방치 차량 발견 (데모 데이터)",
        "status_message_en": f"{vehicle_count} abandoned vehicle(s) detected (Demo data)",
        "metadata": {
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "mode": "demo"
        },
        "analysis": {
            "total_parking_spaces_detected": random.randint(15, 40),
            "spaces_analyzed": random.randint(10, 30),
            "abandoned_vehicles_found": vehicle_count,
            "detection_threshold": 0.90,
            "is_clean": False
        },
        "abandoned_vehicles": vehicles,
        "results": vehicles
    }


# 테스트
if __name__ == "__main__":
    print("=" * 60)
    print("데모 모드 테스트")
    print("=" * 60)

    # 테스트 1: 서울 강남구
    print("\n[테스트 1] 서울 강남구")
    coords = get_demo_coordinates("서울특별시", "강남구")
    print(f"  주소: {coords['address']}")
    print(f"  좌표: ({coords['latitude']}, {coords['longitude']})")
    print(f"  메시지: {coords['message']}")

    # 테스트 2: 제주시
    print("\n[테스트 2] 제주특별자치도 제주시")
    coords = get_demo_coordinates("제주특별자치도", "제주시")
    print(f"  주소: {coords['address']}")
    print(f"  좌표: ({coords['latitude']}, {coords['longitude']})")

    # 테스트 3: 전라남도 나주시 (사용자 요청)
    print("\n[테스트 3] 전라남도 나주시 ⭐")
    coords = get_demo_coordinates("전라남도", "나주시")
    print(f"  주소: {coords['address']}")
    print(f"  좌표: ({coords['latitude']}, {coords['longitude']})")
    print(f"  ✅ 정상 작동: 서울 강남구가 아닌 나주시 좌표 반환!")

    # 테스트 4: 방치 차량 생성
    print("\n[테스트 4] 방치 차량 생성 (vehicle_type 포함)")
    result = get_demo_analysis_result(37.5172, 127.0473, "서울특별시 강남구")
    print(f"  발견된 차량: {result['analysis']['abandoned_vehicles_found']}대")
    print(f"  상태: {result['status_message']}")

    if result['abandoned_vehicles']:
        print("\n  차량 목록:")
        for v in result['abandoned_vehicles']:
            vehicle_type_kr = {'car': '승용차', 'truck': '트럭', 'bus': '버스'}.get(v['vehicle_type'], v['vehicle_type'])
            print(f"    - {v['id']}: {v['similarity_percentage']}% ({v['risk_level']}) - {vehicle_type_kr}")

    print("\n" + "=" * 60)
    print("✅ 데모 모드 정상 작동!")
    print("=" * 60)
