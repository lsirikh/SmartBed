class TypeMessage:
    """
    ᆞTypeMessage : 메시지 타입
    """
    pass

    typeMessage = ''



    def ident(self):
        print('')


class SetActive(TypeMessage):
    """
    수집데이터 전송 요청
    """
    super.typeMessage = ""
    target=0
    range_start=""
    range_end=""
    bed_num=""

    def send(self):
        pass


class User(TypeMessage):
    """
    사용자 정보 설정
    """
    pass


class InfoTime(TypeMessage):
    """
    시간 정보 설정
    """
    pass


class WifiInfo(TypeMessage):
    """
    Wifi 연결 정보 확인 요청
    """
    pass

class WifiSetting(TypeMessage):
    """
    Wifi 연결 정보 설정 요청
    """
    pass

class WifiIP(TypeMessage):
    """
    Wifi IP 정보 설정 요청
    """
    pass


class CloudInfo(TypeMessage):
    """
    클라우드 서버 연결 정보 확인 요청
    """
    pass


class CloudStatus(TypeMessage):
    """
    클라우드 서버 연결 상태 확인 요청
    """
    pass


class CloudInfoSet(TypeMessage):
    """
    클라우드 서버 정보 설정 요청
    """
    pass


class CloudCycleSet(TypeMessage):
    """
    클라우드 서버 데이터 전송주기 설정 요청
    """
    pass


class PressStatus(TypeMessage):
    """
    압력센서 수집모듈 고장 상태 확인
    """
    pass

