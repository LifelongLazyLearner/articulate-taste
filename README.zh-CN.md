# articulate-taste

[![Version](https://img.shields.io/github/v/release/LifelongLazyLearner/articulate-taste?label=version)](https://github.com/LifelongLazyLearner/articulate-taste/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)
[![Language](https://img.shields.io/badge/lang-简体中文-red.svg)](#)
[![GitHub stars](https://img.shields.io/github/stars/LifelongLazyLearner/articulate-taste?style=social)](https://github.com/LifelongLazyLearner/articulate-taste/stargazers)

语言：简体中文 | [English](./README.md)

> *本文与英文版讲同一件事，各自成文。两版对功能和行为的描述如有出入，以英文版为准。*

每个人都有品味，但很少有人说得出自己的品味是什么。

articulate-taste 不问你「你的标准是什么」。它给你看两版东西，你挑一版，标准从你的选择里读出来。像验光：度数你自己说不出，哪片镜片更清楚你一眼就知道。

## 安装

```bash
npx skills@latest add LifelongLazyLearner/articulate-taste -g
```

`-g` 会让你选的 agent 在所有项目里都能用这个技能。安装时还会问你要接到哪个 agent；选 Claude Code，用户级入口就在 `~/.claude/skills/articulate-taste/`。这一步不写画像，画像要等你在某个项目里真跑起来才写。

安装器默认会发送匿名使用数据。不想发送，设置 `DISABLE_TELEMETRY=1`。

装不上就克隆仓库，让 agent 直接读 `SKILL.md`。

## 怎么用

跑 `/articulate-taste`。它一次给你两版，你回 1、2，或者「一样」。

> **1**
> 你这个文件已经大到编辑起来卡了，现在保存一次要八秒左右。
>
> 建议拆成互相链接的多个页面：内容都还能改，代价是没法再一路滚到底。把定稿的部分压成图片会更快，但那些部分就改不动了。
>
> **2**
> 你这个文件已经大到编辑起来卡了，现在保存一次要八秒左右。
>
> 有三条路。拆成互相链接的多个页面，内容都能改，但一路滚到底的视图没了。把定稿的部分压成图片，速度回来，那些部分改不动了。

两版逐句对齐，只差一处：一版给了建议，一版把选项平铺。你回答之前，它不说差别在哪。你多半一眼就知道自己偏哪版，紧接着也说得出为什么。这个「为什么」要是凭空问你，你答不上来。

回「一样」也是答案，说明这个差别对你不起作用，这片镜片就收起来。

选择攒够了，它写成一条原则给你过目：你看重什么，这件事到哪儿为止。措辞你定，不满意整条扔掉。没你点头，什么都进不了画像。

想停随时停。进度不丢，下次接着上次的地方来。

## 你会拿到什么

一份 `TASTE.md`，里面的原则长这样：

```markdown
### recommendation-lowers-entropy — provisional

**Statement.** Say which one you would pick, and carry the reason it rests on.
Laying out options evenly and stopping there leaves the decision cost with the
reader; a recommendation takes some of it back.

**Boundary.** It stops where the reason cannot be given. A bare recommendation
is worse than none. Where you cannot say why, lay out the options and stop.
```

这条不是你说出来的，是两组对比撞出来的。第一组只变「给不给建议」，给建议的那版赢。第二组把同一个差别搬进写的人根本不可能知道答案的场景，给建议的那版输了。边界就落在翻转的那一处，没人需要动嘴描述它。

一次会话结束，它会问你要不要把这份画像打包成独立技能，好让别的项目里的 agent 也用得上。你不开口，它不装任何东西。

## 一条规则：要自证的是工具，不是你

你说你看重什么，就算你看重什么。没人要你拿出做到过的证据，你的答案也不按代价大小排高低。

要挣的是画像本身，两条路。一条，它猜你会怎么评判一件它没见过的东西，你告诉它猜没猜中。另一条，同一件东西写两版，一版背后有画像，一版没有，你盲挑。猜中了，那条原则就更硬一点，因为它证明自己读懂了你。猜错了，该去修的是画像。

## 打包出来的技能会讲理由

接了那个提议，你拿到的技能比一份光秃秃的画像多做一件事：它说明是哪条原则决定了哪个选择。

这是测出来的。默默套用画像产出的东西，主人自己都认不出来，哪怕里面几乎逐字写着他的原则。把理由摆出来，同一个人就认得出了。悄悄用出来的品味，读着不像谁的。

它也不往没请它的项目里凑。第一次在某个地方用，它写一个很小的启用文件；没有这个文件，它对你的东西一句话不说。

## 它不会不问就改

看出矛盾，它有资格把话提出来；没资格改你的画像。

## 局限，先说在前面

猜得准不准，是你打的分。画像看不见自己有没有真读懂你，只能问。这事没沦为走过场，是因为这份画像只有你一个人读，分打松了，你手里就是一份骗自己的文档。

刚做出来的画像最弱。它的底气来自猜对过你，而新的一份一次都还没猜过。

人会给自己的判断编理由。先要选择、后要理由能挡掉一部分，挡不干净。

它记的是你说的，不是你做的。这是故意的：它装的是标准，而标准本来就允许你没做到。别拿它当你的行为描述。

## 其他

- [`SKILL.md`](SKILL.md) 是技能本身，剩下的部分在 [`references/`](references/)。
- 检查一份画像：
  `python3 scripts/taste_profile.py TASTE.md log.md`
