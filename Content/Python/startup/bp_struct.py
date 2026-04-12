import unreal

@unreal.ustruct()
class MaterialSoftObj(unreal.SoftObjectPath):
    pass
    

@unreal.ustruct()
class MaterialWebLinkRow(unreal.TableRowBase):
    """
    데이터 테이블 행 구조 정의: 머티리얼, 설명, 웹링크 매핑
    """
    
    # 방법 1: 커스텀 MaterialSoftObj 사용
    material_ref = unreal.uproperty(MaterialSoftObj, meta={"EditAnywhere": True, "BlueprintReadWrite": True})
    
    # 설명
    description = unreal.uproperty(str, meta={"EditAnywhere": True, "BlueprintReadWrite": True})
    
    # 웹링크 URL
    url = unreal.uproperty(str, meta={"EditAnywhere": True, "BlueprintReadWrite": True})
