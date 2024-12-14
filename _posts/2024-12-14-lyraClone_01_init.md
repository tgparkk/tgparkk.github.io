---
title: "unreal lyra clone: 환경 설정"
header:
  video:
    id: -PVofD2A9t8
    provider: youtube
categories:
  - unreal
  - lyra
tags:
  - unreal
  - lyra
---

형상관리(git)에 필요한 파일 리스트 (리스트는 계속 수정 될거 같아요)

config 폴더
![fileInConfigDir](fileInConfigDir.png)

content 폴더
![fileInContentDir](fileInContentDir.png)

, source 폴더

## Settings

| Parameter  | Required     | Description |
|----------  |---------     | ----------- |
| `id`       | **Required** | ID of the video |
| `provider` | **Required** | Hosting provider of the video, either `youtube` or `vimeo` |

### YouTube

To embed the following YouTube video at url `https://www.youtube.com/watch?v=-PVofD2A9t8` (long version) or `https://youtu.be/-PVofD2A9t8` (short version) into a post or page's main content you'd use: 

```liquid
{% raw %}{% include video id="-PVofD2A9t8" provider="youtube" %}{% endraw %}
```

{% include video id="-PVofD2A9t8" provider="youtube" %}

To embed it as a video header you'd use the following YAML Front Matter

```yaml
header:
  video:
    id: -PVofD2A9t8
    provider: youtube
```

### Vimeo

To embed the following Vimeo video at url `https://vimeo.com/212731897` into a post or page's main content you'd use: 

```liquid
{% raw %}{% include video id="212731897" provider="vimeo" %}{% endraw %}
```

{% include video id="212731897" provider="vimeo" %}

To embed it as a video header you'd use the following YAML Front Matter

```yaml
header:
  video:
    id: 212731897
    provider: vimeo
```