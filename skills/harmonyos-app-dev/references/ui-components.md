# UI 组件参考

> **内容合并自** harmonyos-app 的 arkui.md（完整的组件、@Builder、动画、手势）+ harmonyos-dev 的 ui-components.md（官方文档来源标注 + AlertDialog）
>
> 官方文档：
> - ArkUI 概览: https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-overview
> - 组件开发指南: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkui-ts-components
> - 布局开发: https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-layout-development

## 基础组件

来源: [基础组件](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-components-basic)

### Text

```typescript
Text('Hello World')
  .fontSize(24)
  .fontWeight(FontWeight.Bold)
  .fontColor('#333333')
```

### Image

```typescript
Image($r('app.media.icon'))
  .width(100)
  .height(100)
  .objectFit(ImageFit.Cover)
  .fillColor($r('sys.color.brand'))  // 模板模式着色
```

### Button

```typescript
Button('Click Me')
  .type(ButtonType.Capsule)
  .width(200)
  .height(48)
  .onClick(() => {
    console.info('Button clicked');
  })
```

### TextInput

```typescript
TextInput({ placeholder: 'Enter text' })
  .width('100%')
  .height(48)
  .onChange((value: string) => {
    this.inputValue = value;
  })
```

---

## 布局容器

来源: [布局开发指导](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-layout-development)

### Column（垂直布局）

来源: [Column容器](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-container-column)

```typescript
Column() {
  Text('Item 1')
  Text('Item 2')
  Text('Item 3')
}
.width('100%')
.alignItems(HorizontalAlign.Center)
.justifyContent(FlexAlign.SpaceBetween)
```

### Row（水平布局）

来源: [Row容器](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-container-row)

```typescript
Row() {
  Image($r('app.media.avatar')).width(48).height(48)
  Text('Username').margin({ left: 12 })
  Blank()  // 弹性空间
  Image($r('app.media.arrow'))
}
.width('100%')
.padding(16)
```

### Stack（堆叠布局）

来源: [Stack容器](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-container-stack)

```typescript
Stack({ alignContent: Alignment.BottomEnd }) {
  Image($r('app.media.photo'))
  Badge({ count: 5 })
}
```

### Flex（弹性布局）

```typescript
Flex({
  direction: FlexDirection.Row,
  wrap: FlexWrap.Wrap,
  justifyContent: FlexAlign.SpaceAround
}) {
  ForEach(this.items, (item: Item) => {
    ItemCard({ item: item })
  })
}
```

### Grid（网格布局）

来源: [Grid容器](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-container-grid)

```typescript
Grid() {
  ForEach(this.products, (product: Product) => {
    GridItem() {
      ProductCard({ product: product })
    }
  })
}
.columnsTemplate('1fr 1fr')  // 2 列
.rowsGap(12)
.columnsGap(12)
```

---

## 列表与渲染控制

来源: [渲染控制](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-rendering-control)

### ForEach

来源: [ForEach使用](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-rendering-control-foreach)

```typescript
ForEach(this.items, (item: Item, index: number) => {
  ListItem() {
    Text(item.name)
  }
}, (item: Item) => item.id)  // 第三个参数是 key 生成器
```

### LazyForEach（懒加载，推荐用于长列表）

来源: [LazyForEach使用](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-rendering-control-lazyforeach)

```typescript
LazyForEach(this.dataSource, (item: Item) => {
  ListItem() {
    ItemCard({ item: item })
  }
}, (item: Item) => item.id)
```

### List 完整示例

```typescript
List() {
  ForEach(this.dataList, (item: DataItem, index: number) => {
    ListItem() {
      Text(item.name)
    }
  }, (item: DataItem) => item.id)
}
.width('100%')
.divider({ strokeWidth: 1, color: '#E8E8E8' })
```

### Swipe Actions（侧滑操作）

```typescript
List() {
  ForEach(this.items, (item: Item) => {
    ListItem() {
      ItemRow({ item: item })
    }
    .swipeAction({
      end: this.DeleteButton(item.id)
    })
  })
}

@Builder
DeleteButton(id: string) {
  Button('Delete')
    .backgroundColor(Color.Red)
    .onClick(() => this.deleteItem(id))
}
```

### WaterFlow（瀑布流布局）

```typescript
WaterFlow() {
  ForEach(this.images, (image: ImageData) => {
    FlowItem() {
      Image(image.url)
        .width('100%')
        .aspectRatio(image.aspectRatio)
    }
  })
}
.columnsTemplate('1fr 1fr')
```

---

## 滚动与导航容器

### Scroll

```typescript
Scroll() {
  Column() {
    ForEach(this.items, (item: Item) => {
      ItemCard({ item: item })
    })
  }
}
.scrollable(ScrollDirection.Vertical)
.scrollBar(BarState.Auto)
.edgeEffect(EdgeEffect.Spring)
```

### Swiper（轮播）

```typescript
Swiper() {
  ForEach(this.banners, (banner: Banner) => {
    Image(banner.imageUrl)
      .width('100%')
      .height(200)
  })
}
.autoPlay(true)
.interval(3000)
.indicator(true)
```

### Tabs

来源: [Tabs组件](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-container-tabs)

```typescript
Tabs({ barPosition: BarPosition.Start }) {
  TabContent() { HomeTab() }.tabBar('Home')
  TabContent() { DiscoverTab() }.tabBar('Discover')
  TabContent() { ProfileTab() }.tabBar('Profile')
}
.barMode(BarMode.Fixed)
.onChange((index: number) => {
  this.currentTab = index;
})
```

---

## 自定义组件

### 基础自定义组件

```typescript
@Component
struct UserCard {
  @Prop username: string = '';
  @Prop avatarUrl: string = '';
  @State isFollowing: boolean = false;

  build() {
    Row() {
      Image(this.avatarUrl)
        .width(48).height(48)
        .borderRadius(24)

      Column() {
        Text(this.username)
          .fontSize(16)
          .fontWeight(FontWeight.Medium)
      }
      .margin({ left: 12 })
      .alignItems(HorizontalAlign.Start)

      Blank()

      Button(this.isFollowing ? 'Following' : 'Follow')
        .onClick(() => { this.isFollowing = !this.isFollowing; })
    }
    .width('100%')
    .padding(16)
  }
}
```

### @Builder 函数（局部 UI 复用）

```typescript
@Component
struct ProductList {
  @State products: Product[] = [];

  @Builder
  ProductItem(product: Product) {
    Row() {
      Image(product.imageUrl).width(80).height(80)
      Column() {
        Text(product.name)
        Text(`$${product.price}`).fontColor('#FF6B00')
      }
    }
  }

  @Builder
  SectionHeader(title: string) {
    Text(title)
      .fontSize(18).fontWeight(FontWeight.Bold)
      .margin({ top: 16, bottom: 8 })
  }

  build() {
    List() {
      ListItem() { this.SectionHeader('Featured Products') }
      ForEach(this.products, (product: Product) => {
        ListItem() { this.ProductItem(product) }
      })
    }
  }
}
```

### @BuilderParam（插槽）

```typescript
@Component
struct Card {
  @BuilderParam content: () => void = this.defaultContent;
  @BuilderParam footer: () => void = this.defaultFooter;

  @Builder defaultContent() { Text('Default content') }
  @Builder defaultFooter() {}

  build() {
    Column() {
      this.content()  // 内容插槽
      this.footer()   // 底部插槽
    }
    .padding(16)
    .backgroundColor(Color.White)
    .borderRadius(8)
  }
}

// 使用
@Component
struct ProductPage {
  build() {
    Card() {
      // 内容
      Column() {
        Image($r('app.media.product'))
        Text('Product Name')
      }
    }
    .footer(() => {
      Row() {
        Button('Add to Cart')
        Button('Buy Now')
      }
    })
  }
}
```

### @Styles 和 @Extend（样式复用）

```typescript
// 通用样式（@Styles）
@Styles
function cardStyle() {
  .backgroundColor(Color.White)
  .borderRadius(12)
  .shadow({ radius: 8, color: '#1A000000' })
  .padding(16)
}

@Styles
function centerStyle() {
  .width('100%')
  .alignItems(HorizontalAlign.Center)
  .justifyContent(FlexAlign.Center)
}

// 特定组件扩展（@Extend）
@Extend(Text)
function titleStyle() {
  .fontSize(24)
  .fontWeight(FontWeight.Bold)
  .fontColor('#1A1A1A')
}

@Extend(Button)
function primaryButton() {
  .type(ButtonType.Capsule)
  .backgroundColor('#007AFF')
  .fontColor(Color.White)
  .width('100%')
  .height(48)
}

// 使用
Column() {
  Text('Welcome').titleStyle()
  Button('Get Started').primaryButton()
}.cardStyle()
```

---

## 对话框与弹窗

来源: [弹窗开发指导](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-popup-and-menu)

### CustomDialog（自定义对话框）

来源: [CustomDialog](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-components-customdialog)

```typescript
@CustomDialog
struct ConfirmDialog {
  controller: CustomDialogController;
  title: string = '';
  message: string = '';
  onConfirm: () => void = () => {};
  onCancel: () => void = () => {};

  build() {
    Column() {
      Text(this.title)
        .fontSize(18).fontWeight(FontWeight.Bold)
      Text(this.message).margin({ top: 16 })
      Row() {
        Button('Cancel').onClick(() => this.onCancel())
        Button('Confirm').onClick(() => this.onConfirm())
      }
      .margin({ top: 24 })
      .justifyContent(FlexAlign.SpaceEvenly)
      .width('100%')
    }
    .padding(24)
  }
}

// 使用
@Component
struct DialogDemo {
  dialogController: CustomDialogController = new CustomDialogController({
    builder: ConfirmDialog({
      title: 'Confirm',
      message: 'Are you sure?',
      onConfirm: () => this.handleConfirm(),
      onCancel: () => this.dialogController.close()
    }),
    autoCancel: true,
    alignment: DialogAlignment.Center
  });

  handleConfirm(): void {
    // 处理确认
    this.dialogController.close();
  }

  build() {
    Button('Show Dialog')
      .onClick(() => { this.dialogController.open(); })
  }
}
```

### AlertDialog（系统警告框）

来源: [AlertDialog](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkui-ts-components-alertdialog)

```typescript
AlertDialog.show({
  title: '提示',
  message: '确定要删除吗？',
  primaryButton: {
    value: '取消',
    action: () => {}
  },
  secondaryButton: {
    value: '确定',
    action: () => { /* 删除逻辑 */ }
  }
})
```

---

## 动画

来源: [动画开发指导](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-animation)

### 属性动画

来源: [属性动画](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-property-animation)

```typescript
@Component
struct AnimatedButton {
  @State scale: number = 1;
  @State opacity: number = 1;

  build() {
    Button('Animated')
      .scale({ x: this.scale, y: this.scale })
      .opacity(this.opacity)
      .animation({
        duration: 300,
        curve: Curve.EaseInOut
      })
      .onTouch((event: TouchEvent) => {
        if (event.type === TouchType.Down) {
          this.scale = 0.95;
          this.opacity = 0.8;
        } else if (event.type === TouchType.Up) {
          this.scale = 1;
          this.opacity = 1;
        }
      })
  }
}
```

### 显式动画

```typescript
animateTo({
  duration: 1000,
  curve: Curve.EaseInOut,
  iterations: 1,
  playMode: PlayMode.Normal
}, () => {
  this.rotateAngle = 360;
  this.translateY = 100;
})
```

### 转场动画

来源: [转场动画](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-transition-animation)

```typescript
if (this.isVisible) {
  Text('Animated Content')
    .transition({
      type: TransitionType.Insert,
      opacity: 0,
      translate: { y: 50 }
    })
    .transition({
      type: TransitionType.Delete,
      opacity: 0,
      scale: { x: 0.8, y: 0.8 }
    })
}
```

### 共享元素转场

来源: [共享元素转场](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-shared-element-transition)

```typescript
this.uiContext.pushPath({ name: 'Detail' }, null);
```

---

## 手势

```typescript
@Component
struct GestureDemo {
  @State offsetX: number = 0;
  @State offsetY: number = 0;
  @State scale: number = 1;

  build() {
    Image($r('app.media.photo'))
      .translate({ x: this.offsetX, y: this.offsetY })
      .scale({ x: this.scale, y: this.scale })
      // 拖动手势
      .gesture(
        PanGesture()
          .onActionUpdate((event: GestureEvent) => {
            this.offsetX = event.offsetX;
            this.offsetY = event.offsetY;
          })
      )
      // 缩放手势
      .gesture(
        PinchGesture({ fingers: 2 })
          .onActionUpdate((event: GestureEvent) => {
            this.scale = event.scale;
          })
      )
      // 组合手势
      .gesture(
        GestureGroup(GestureMode.Parallel,
          TapGesture({ count: 2 })
            .onAction(() => { this.scale = this.scale === 1 ? 2 : 1; }),
          LongPressGesture()
            .onAction(() => { /* 显示菜单 */ })
        )
      )
  }
}
```

---

## 样式系统

来源: [资源使用指导](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-resource)

### 系统资源

来源: [系统资源](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-system-resource)

```typescript
$r('sys.color.brand')                          // 品牌色
$r('sys.color.ohos_id_color_text_primary')     // 主文本色
$r('sys.media.ohos_ic_public_ok')              // 系统图标
```

### 主题与模糊效果

```typescript
.backgroundBlurStyle(BlurStyle.COMPONENT_THIN)
```

### 响应式断点

来源: [响应式布局](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-responsive-layout)

```typescript
.breakpoints({
  sm: { value: 600 },
  md: { value: 840 },
  lg: { value: 1280 }
})
```

### 响应式布局示例

```typescript
@Component
struct ResponsiveLayout {
  @StorageProp('currentBreakpoint') currentBreakpoint: string = 'sm';

  build() {
    GridRow({
      columns: { sm: 4, md: 8, lg: 12 },
      gutter: { x: 12, y: 12 }
    }) {
      GridCol({ span: { sm: 4, md: 4, lg: 3 } }) {
        this.Sidebar()
      }
      GridCol({ span: { sm: 4, md: 4, lg: 9 } }) {
        this.MainContent()
      }
    }
  }

  @Builder Sidebar() {
    Column() { /* 侧边栏内容 */ }
      .visibility(this.currentBreakpoint === 'sm'
        ? Visibility.None : Visibility.Visible)
  }

  @Builder MainContent() {
    Column() { /* 主内容 */ }
  }
}
```

---

## 最佳实践

### 组件设计

```typescript
// ✅ 单一职责，可复用
@Component
struct Avatar {
  @Prop src: string = '';
  @Prop size: number = 48;
  @Prop borderRadius: number = 24;

  build() {
    Image(this.src)
      .width(this.size).height(this.size)
      .borderRadius(this.borderRadius)
      .objectFit(ImageFit.Cover)
  }
}

// ✅ 组合优先于继承
@Component
struct UserProfile {
  @Prop user: User = new User();

  build() {
    Row() {
      Avatar({ src: this.user.avatar, size: 64 })
      Column() {
        Text(this.user.name)
        Text(this.user.bio)
      }
    }
  }
}
```

### 性能要点

```typescript
// ✅ 长列表用 LazyForEach
LazyForEach(this.dataSource, (item: Item) => {
  ListItem() { ItemCard({ item: item }) }
}, (item: Item) => item.id)

// ✅ ForEach 必须提供 key 函数
ForEach(this.items, (item: Item, index: number) => {
  ItemRow({ item: item })
}, (item: Item) => item.id)

// ✅ 使用 @Watch 监听变化
@Component
struct OptimizedList {
  @State @Watch('onDataChange') items: Item[] = [];

  onDataChange(): void {
    // 仅在 items 实际变化时调用
  }
}
```