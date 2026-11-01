"""Fail-closed release gate. This module does not upload or publish anything."""
import hashlib,json,sys
from pathlib import Path

def problems(record,media):
    p=Path(media); errors=[]
    if not p.is_file():return ['missing_mp4']
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    for section in ('technical','editorial','rights','youtube'):
        if not isinstance(record.get(section),dict):errors.append('missing_'+section)
    tech=record.get('technical',{});edit=record.get('editorial',{})
    rights=record.get('rights',{});yt=record.get('youtube',{})
    if tech.get('sha256')!=digest:errors.append('technical_review_wrong_file')
    if edit.get('sha256')!=digest:errors.append('editorial_review_wrong_file')
    for key in ('decode_pass','no_black_defects','no_audio_defects','captions_pass'):
        if tech.get(key) is not True:errors.append(key)
    for key in ('full_viewing','full_listening','story_pass','car_identity_pass','no_misleading_claims'):
        if edit.get(key) is not True:errors.append(key)
    if not edit.get('reviewed_by') or not edit.get('reviewed_at'):errors.append('editorial_review_missing_identity_or_time')
    if rights.get('all_assets_cleared') is not True:errors.append('rights_not_cleared')
    if record.get('requires_real_engine') and rights.get('model_matched_real_engine_audio') is not True:errors.append('real_engine_missing')
    if yt.get('privacy') not in ('private','scheduled'):errors.append('private_upload_not_verified')
    if yt.get('copyright_checks')!='complete_no_issues':errors.append('copyright_not_clear')
    if yt.get('hd_complete') is not True:errors.append('hd_incomplete')
    if yt.get('unresolved_claims',True) is not False:errors.append('claims_not_clear')
    if not yt.get('video_id'):errors.append('missing_youtube_id')
    if record.get('publication_authorized') is not True:errors.append('publication_not_authorized')
    return errors

if __name__=='__main__':
    record=json.loads(Path(sys.argv[1]).read_text())
    e=problems(record,sys.argv[2]);print(json.dumps({'release_allowed':not e,'blockers':e},indent=2));sys.exit(bool(e))
