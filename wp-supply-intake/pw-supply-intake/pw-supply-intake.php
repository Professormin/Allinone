<?php
/*
Plugin Name: 种苗及鲜切花供货征集（Supply Intake）
Description: 欧美回购牡丹芍药种苗信息征集表。前台页面：网址/supply/（或 网址/?pw_supply=1）；后台菜单「种苗征集」查看每份提交、照片，导出 CSV。
Version: 1.1.0
Author: Professormin
License: MIT
Plugin URI: https://github.com/Professormin/allinone/tree/main/wp-supply-intake
*/
if (!defined('ABSPATH')) exit;

function pws_register() {
  register_post_type('pw_supply', ['label' => '种苗征集', 'public' => false, 'show_ui' => false, 'supports' => ['title']]);
  add_rewrite_rule('^supply/?$', 'index.php?pw_supply_page=1', 'top');
}
add_action('init', 'pws_register');
add_filter('query_vars', function ($v) { $v[] = 'pw_supply_page'; return $v; });
register_activation_hook(__FILE__, function () { pws_register(); flush_rewrite_rules(); });
register_deactivation_hook(__FILE__, function () { flush_rewrite_rules(); });

/* ---------- 前台页面 ---------- */
add_action('template_redirect', function () {
  if (!get_query_var('pw_supply_page') && !isset($_GET['pw_supply'])) return;
  $html = file_get_contents(__DIR__ . '/form.html');
  $cfg = 'window.PWS_API=' . wp_json_encode(rest_url('pw-supply/v1/')) . ';';
  $html = str_replace('/*PWS_CONFIG*/', $cfg, $html);
  nocache_headers();
  header('Content-Type: text/html; charset=utf-8');
  echo $html;
  exit;
});

/* ---------- 接收接口 ---------- */
add_action('rest_api_init', function () {
  register_rest_route('pw-supply/v1', '/submit', ['methods' => 'POST', 'callback' => 'pws_submit', 'permission_callback' => '__return_true']);
  register_rest_route('pw-supply/v1', '/photo', ['methods' => 'POST', 'callback' => 'pws_photo', 'permission_callback' => '__return_true']);
});

function pws_clean($v) {
  if (is_array($v)) return array_map('pws_clean', $v);
  if (is_bool($v) || is_int($v) || is_float($v) || $v === null) return $v;
  return sanitize_textarea_field((string)$v);
}

function pws_submit(WP_REST_Request $r) {
  $d = $r->get_json_params();
  if (!is_array($d) || !empty($d['hp'])) return new WP_Error('bad', '提交格式不对', ['status' => 400]);
  $ip = $_SERVER['REMOTE_ADDR'] ?? '';
  $k = 'pws_rl_' . md5($ip);
  $n = (int)get_transient($k);
  if ($n >= 30) return new WP_Error('busy', '提交太频繁，请一小时后再试', ['status' => 429]);
  set_transient($k, $n + 1, HOUR_IN_SECONDS);
  $sup = pws_clean($d['sup'] ?? []);
  $items = pws_clean(array_slice((array)($d['items'] ?? []), 0, 300));
  if (empty($sup['boss']) || empty($sup['tel'])) return new WP_Error('bad', '缺少联系人或电话', ['status' => 400]);
  if (!$items) return new WP_Error('bad', '没有品种', ['status' => 400]);
  $title = trim(($sup['farm'] ?? '') . ' ' . ($sup['boss'] ?? '') . ' ' . ($sup['tel'] ?? ''));
  $id = wp_insert_post(['post_type' => 'pw_supply', 'post_status' => 'private', 'post_title' => $title], true);
  if (is_wp_error($id)) return $id;
  $token = wp_generate_password(24, false);
  update_post_meta($id, '_pws_data', wp_slash(wp_json_encode(['sup' => $sup, 'items' => $items], JSON_UNESCAPED_UNICODE)));
  update_post_meta($id, '_pws_token', $token);
  update_post_meta($id, '_pws_photos', []);
  update_post_meta($id, '_pws_ip', $ip);
  return ['id' => $id, 'token' => $token];
}

function pws_photo(WP_REST_Request $r) {
  $id = (int)$r->get_param('id');
  $key = preg_replace('/[^a-z0-9\-]/', '', (string)$r->get_param('key'));
  if (!$id || get_post_type($id) !== 'pw_supply' || !hash_equals((string)get_post_meta($id, '_pws_token', true), (string)$r->get_param('token')))
    return new WP_Error('bad', '无效的提交编号', ['status' => 403]);
  $photos = (array)get_post_meta($id, '_pws_photos', true);
  if (count($photos) >= 300) return new WP_Error('bad', '照片太多', ['status' => 400]);
  $f = $r->get_file_params()['file'] ?? null;
  if (!$f || $f['error'] || $f['size'] > 5 * 1024 * 1024 || !@getimagesize($f['tmp_name'])) return new WP_Error('bad', '不是有效的图片', ['status' => 400]);
  require_once ABSPATH . 'wp-admin/includes/file.php';
  require_once ABSPATH . 'wp-admin/includes/media.php';
  require_once ABSPATH . 'wp-admin/includes/image.php';
  $f['name'] = 'supply-' . $id . '-' . $key . '.jpg';
  $aid = media_handle_sideload($f, $id, get_the_title($id) . ' ' . $key);
  if (is_wp_error($aid)) return $aid;
  $photos[$key] = $aid;
  update_post_meta($id, '_pws_photos', $photos);
  return ['ok' => true];
}

/* ---------- 后台 ---------- */
add_action('admin_menu', function () {
  add_menu_page('种苗征集', '种苗征集', 'manage_options', 'pw-supply', 'pws_admin', 'dashicons-clipboard', 26);
});
function pws_kind($it) { $m = ['normal' => '商业栽培品种', 'import' => '高单价进口品种', 'new' => '独家新品种']; return $m[$it['kind'] ?? 'normal'] ?? '商业栽培品种'; }
function pws_get($id) {
  $d = json_decode((string)get_post_meta($id, '_pws_data', true), true) ?: ['sup' => [], 'items' => []];
  $d['photos'] = (array)get_post_meta($id, '_pws_photos', true);
  return $d;
}
function pws_img($aid, $sz = 90) {
  return '<a href="' . esc_url(wp_get_attachment_url($aid)) . '" target="_blank">' . wp_get_attachment_image($aid, [$sz, $sz], false, ['style' => "width:{$sz}px;height:{$sz}px;object-fit:cover;border-radius:6px;margin:2px"]) . '</a>';
}
function pws_item_photos($photos, $i) { $o = ''; foreach ($photos as $k => $aid) if (strpos($k, "i$i-") === 0) $o .= pws_img($aid); return $o ?: '<span style="color:#999">无</span>'; }
function pws_grade($it) { $g = $it['grade'] ?? ''; return $g === '—' ? '文字描述' : ($g ? $g . ' 级' : ''); }
/* 把一个品种的可供方式按 原棵/分株苗/鲜切花 分开成文字 */
function pws_offers($it) {
  $o = ['原棵' => [], '分株苗' => [], '鲜切花' => []];
  if (!empty($it['offers'])) {
    foreach ($it['offers'] as $x) $o[$x['mode']][] = trim(($x['spec'] ?? '') . ' ' . number_format((float)$x['qty']) . ($x['unit'] ?? '') . ' · ' . $x['price'] . '元/' . ($x['unit'] ?? ''));
  } elseif (!empty($it['specText'])) { // 旧版提交
    $mode = (($it['unit'] ?? '') === '棵') ? '原棵' : '分株苗';
    $o[$mode][] = $it['specText'] . ' ' . ($it['qty'] ?? '') . ($it['unit'] ?? '') . ' · ' . ($it['price'] ?? '') . '元/' . ($it['unit'] ?? '');
  }
  if (!empty($it['harvest']) && $o['鲜切花']) $o['鲜切花'][] = '采收：' . implode('、', (array)$it['harvest']);
  return $o;
}
function pws_newplants($it) { return implode('、', array_map(fn($p) => ($p['age'] ?? '?') . '年生' . ($p['n'] ?? '?') . '株', array_filter((array)($it['plants'] ?? []), fn($p) => !empty($p['age']) || !empty($p['n'])))); }
function pws_supline($s) { $t = []; if (!empty($s['area'])) $t[] = $s['area'] . '亩'; if (!empty($s['vcount'])) $t[] = $s['vcount'] . '个品种'; if (!empty($s['types'])) $t[] = '能供：' . implode('/', (array)$s['types']); return implode(' · ', $t); }

function pws_admin() {
  if (!current_user_can('manage_options')) return;
  $base = admin_url('admin.php?page=pw-supply');
  echo '<div class="wrap"><h1>种苗及鲜切花供货征集</h1>';
  echo '<p>发给老板的链接：<a href="' . esc_url(home_url('/supply/')) . '" target="_blank">' . esc_html(home_url('/supply/')) . '</a>（备用 ' . esc_html(home_url('/?pw_supply=1')) . '）</p>';
  if (!empty($_GET['deleted'])) echo '<div class="notice notice-success"><p>已删除。</p></div>';
  $exp = wp_nonce_url(admin_url('admin-post.php?action=pws_export'), 'pws_export');
  echo '<p><a class="button" href="' . esc_url($base) . '">按苗圃看</a> <a class="button" href="' . esc_url($base . '&view=all') . '">全部品种总表</a> <a class="button button-primary" href="' . esc_url($exp) . '">导出 Excel（CSV）</a></p>';
  if (($_GET['view'] ?? '') === 'all') { pws_admin_all(); echo '</div>'; return; }
  if (!empty($_GET['view'])) { pws_admin_view((int)$_GET['view']); echo '</div>'; return; }
  $q = get_posts(['post_type' => 'pw_supply', 'post_status' => 'private', 'numberposts' => 500]);
  echo '<table class="widefat striped"><thead><tr><th>编号</th><th>提交时间</th><th>苗圃 / 联系人</th><th>电话</th><th>地址</th><th>总面积 · 品种数</th><th>已填品种</th><th>新品种</th><th>照片</th><th></th></tr></thead><tbody>';
  if (!$q) echo '<tr><td colspan="10">还没有提交</td></tr>';
  foreach ($q as $p) {
    $d = pws_get($p->ID); $s = $d['sup'];
    $nn = count(array_filter($d['items'], fn($x) => ($x['kind'] ?? '') === 'new'));
    printf('<tr><td>%d</td><td>%s</td><td><b>%s</b> %s</td><td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td><a class="button" href="%s">查看</a></td></tr>',
      $p->ID, esc_html(get_the_date('Y-m-d H:i', $p)), esc_html($s['farm'] ?? ''), esc_html($s['boss'] ?? ''), esc_html($s['tel'] ?? ''), esc_html($s['addr'] ?? ''), esc_html(pws_supline($s)),
      count($d['items']) - $nn, $nn, count($d['photos']), esc_url($base . '&view=' . $p->ID));
  }
  echo '</tbody></table>';
}

function pws_admin_view($id) {
  if (get_post_type($id) !== 'pw_supply') { echo '<p>找不到这份提交</p>'; return; }
  $d = pws_get($id); $s = $d['sup']; $ph = $d['photos'];
  printf('<h2>#%d　%s %s</h2><p>电话 / 微信：%s　　地址：%s　　%s　　提交时间：%s</p>', $id, esc_html($s['farm'] ?? ''), esc_html($s['boss'] ?? ''), esc_html($s['tel'] ?? ''), esc_html($s['addr'] ?? ''), esc_html(pws_supline($s)), esc_html(get_the_date('Y-m-d H:i', $id)));
  $sp = ''; foreach ($ph as $k => $aid) if (strpos($k, 'sup-') === 0) $sp .= pws_img($aid);
  if ($sp) echo '<h3>苗圃规模 / 经营照片</h3><div>' . $sp . '</div>';
  echo '<h3>品种</h3><table class="widefat striped"><thead><tr><th>#</th><th>品种</th><th>类型</th><th>等级</th><th>种植</th><th>原棵</th><th>分株苗</th><th>鲜切花</th><th>地块 / 水淹</th><th>描述</th><th>照片</th></tr></thead><tbody>';
  foreach ($d['items'] as $i => $it) {
    if (($it['kind'] ?? '') === 'new') continue;
    $o = pws_offers($it);
    printf('<tr><td>%d</td><td><b>%s</b>%s<br><small>%s</small></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s / %s</td><td style="max-width:220px">%s</td><td>%s</td></tr>',
      $i + 1, esc_html($it['name'] ?? ''), empty($it['en']) ? '' : '<br><small>' . esc_html($it['en']) . '</small>', esc_html($it['cat'] ?? ''), esc_html(pws_kind($it)), esc_html(pws_grade($it)),
      esc_html($it['plantText'] ?? ''), implode('<br>', array_map('esc_html', $o['原棵'])) ?: '—', implode('<br>', array_map('esc_html', $o['分株苗'])) ?: '—', implode('<br>', array_map('esc_html', $o['鲜切花'])) ?: '—',
      esc_html(($it['land'] ?? '') ?: '—'), esc_html(($it['flood'] ?? '') ?: '—'), nl2br(esc_html($it['desc'] ?? '')), pws_item_photos($ph, $i));
  }
  echo '</tbody></table>';
  $new = array_filter($d['items'], fn($x) => ($x['kind'] ?? '') === 'new');
  if ($new) {
    echo '<h3>独家新品种</h3><table class="widefat striped"><thead><tr><th>#</th><th>品种</th><th>等级</th><th>类群</th><th>育种者</th><th>亲本</th><th>年份</th><th>现有植株</th><th>可提供</th><th>特点</th><th>照片</th></tr></thead><tbody>';
    foreach ($new as $i => $it) {
      printf('<tr><td>%d</td><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s × %s</td><td>杂交 %s / 首花 %s</td><td>%s</td><td>%s 株</td><td style="max-width:220px">%s（曾对外销售：%s）</td><td>%s</td></tr>',
        $i + 1, esc_html($it['name'] ?? ''), esc_html(pws_grade($it)), esc_html($it['cat'] ?? ''), esc_html($it['breeder'] ?? ''),
        esc_html(($it['mom'] ?? '') ?: '?'), esc_html(($it['dad'] ?? '') ?: '?'), esc_html(($it['crossYear'] ?? '') ?: '?'), esc_html(($it['flowerYear'] ?? '') ?: '?'), esc_html(pws_newplants($it) ?: '未填'), esc_html(($it['offer'] ?? '') ?: '?'), esc_html($it['note'] ?? ''), esc_html($it['sold'] ?? ''), pws_item_photos($ph, $i));
    }
    echo '</tbody></table>';
  }
  $del = wp_nonce_url(admin_url('admin-post.php?action=pws_delete&id=' . $id), 'pws_delete_' . $id);
  echo '<p style="margin-top:24px"><a class="button" style="color:#b32d2e" href="' . esc_url($del) . '" onclick="return confirm(\'确定删除这份提交和它的照片？删除后不能恢复。\')">删除这份提交</a></p>';
}

/* 全部品种总表：可筛选、可按品种合并 */
function pws_admin_all() {
  $mode = sanitize_key($_GET['mode'] ?? ''); $merge = !empty($_GET['merge']);
  $base = admin_url('admin.php?page=pw-supply&view=all');
  $btn = function ($label, $args, $on) use ($base) { echo '<a class="button' . ($on ? ' button-primary' : '') . '" href="' . esc_url(add_query_arg($args, $base)) . '">' . esc_html($label) . '</a> '; };
  echo '<p>'; $btn('全部', [], !$mode && !$merge); $btn('只看鲜切花', ['mode' => 'cut'], $mode === 'cut'); $btn('只看种苗', ['mode' => 'seed'], $mode === 'seed'); $btn('只看独家新品种', ['mode' => 'new'], $mode === 'new'); $btn('按品种合并', ['merge' => 1, 'mode' => $mode], $merge); echo '</p>';
  $rows = [];
  foreach (get_posts(['post_type' => 'pw_supply', 'post_status' => 'private', 'numberposts' => -1]) as $p) {
    $d = pws_get($p->ID); $s = $d['sup'];
    foreach ($d['items'] as $i => $it) {
      $nw = ($it['kind'] ?? '') === 'new'; $o = pws_offers($it);
      if ($mode === 'new' && !$nw) continue;
      if ($mode === 'cut' && (!$o['鲜切花'] || $nw)) continue;
      if ($mode === 'seed' && ((!$o['原棵'] && !$o['分株苗']) || $nw)) continue;
      $rows[] = compact('p', 's', 'it', 'o', 'nw', 'i') + ['ph' => $d['photos']];
    }
  }
  if ($merge) {
    $g = [];
    foreach ($rows as $r) {
      $k = $r['it']['name'] ?? ''; $g[$k] = $g[$k] ?? ['n' => 0, 'mu' => 0, 'farms' => [], 'm' => ['原棵' => [0, '棵'], '分株苗' => [0, '苗'], '鲜切花' => [0, '支']], 'price' => ['原棵' => [], '分株苗' => [], '鲜切花' => []]];
      $g[$k]['n'] += (float)($r['it']['plantN'] ?? 0); $g[$k]['mu'] += (float)($r['it']['plantMu'] ?? 0); $g[$k]['farms'][] = ($r['s']['farm'] ?? '') ?: ($r['s']['boss'] ?? '');
      foreach ((array)($r['it']['offers'] ?? []) as $x) { $g[$k]['m'][$x['mode']][0] += (float)$x['qty']; $g[$k]['price'][$x['mode']][] = (float)$x['price']; }
    }
    ksort($g);
    echo '<table class="widefat striped"><thead><tr><th>品种</th><th>几家</th><th>亩</th><th>种植棵数</th><th>原棵</th><th>分株苗</th><th>鲜切花</th><th>苗圃</th></tr></thead><tbody>';
    foreach ($g as $k => $v) {
      $cell = function ($m) use ($v) { [$q, $u] = $v['m'][$m]; if (!$q) return '—'; $pr = $v['price'][$m]; return number_format($q) . $u . ' · ' . (min($pr) == max($pr) ? min($pr) : min($pr) . '–' . max($pr)) . '元/' . $u; };
      printf('<tr><td><b>%s</b></td><td>%d</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>', esc_html($k), count(array_unique($v['farms'])), esc_html(round($v['mu'], 1)), esc_html(number_format($v['n'])), esc_html($cell('原棵')), esc_html($cell('分株苗')), esc_html($cell('鲜切花')), esc_html(implode('、', array_unique($v['farms']))));
    }
    echo '</tbody></table>'; return;
  }
  echo '<table class="widefat striped"><thead><tr><th>苗圃 / 联系人</th><th>品种</th><th>类型</th><th>亩</th><th>种植棵数</th><th>种植明细</th><th>原棵</th><th>分株苗</th><th>鲜切花</th><th>等级</th><th>照片</th></tr></thead><tbody>';
  if (!$rows) echo '<tr><td colspan="11">没有符合的品种</td></tr>';
  foreach ($rows as $r) {
    $it = $r['it']; $o = $r['o'];
    printf('<tr><td><a href="%s"><b>%s</b></a> %s<br><small>%s</small></td><td><b>%s</b>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>',
      esc_url(admin_url('admin.php?page=pw-supply&view=' . $r['p']->ID)), esc_html($r['s']['farm'] ?? ''), esc_html($r['s']['boss'] ?? ''), esc_html($r['s']['tel'] ?? ''),
      esc_html($it['name'] ?? ''), empty($it['en']) ? '' : '<br><small>' . esc_html($it['en']) . '</small>', esc_html(pws_kind($it)),
      esc_html($r['nw'] ? '' : ($it['plantMu'] ?? '')), esc_html($r['nw'] ? pws_newplants($it) : number_format((float)($it['plantN'] ?? 0))), esc_html($it['plantText'] ?? ''),
      implode('<br>', array_map('esc_html', $o['原棵'])) ?: '—', implode('<br>', array_map('esc_html', $o['分株苗'])) ?: '—', implode('<br>', array_map('esc_html', $o['鲜切花'])) ?: '—',
      esc_html(pws_grade($it)), pws_item_photos($r['ph'], $r['i']));
  }
  echo '</tbody></table>';
}

add_action('admin_post_pws_delete', function () {
  $id = (int)($_GET['id'] ?? 0);
  if (!current_user_can('manage_options') || !check_admin_referer('pws_delete_' . $id) || get_post_type($id) !== 'pw_supply') wp_die('无权限');
  foreach ((array)get_post_meta($id, '_pws_photos', true) as $aid) wp_delete_attachment((int)$aid, true);
  wp_delete_post($id, true);
  wp_safe_redirect(admin_url('admin.php?page=pw-supply&deleted=1')); exit;
});

add_action('admin_post_pws_export', function () {
  if (!current_user_can('manage_options') || !check_admin_referer('pws_export')) wp_die('无权限');
  header('Content-Type: text/csv; charset=utf-8');
  header('Content-Disposition: attachment; filename=供货征集_' . date('Ymd_Hi') . '.csv');
  $o = fopen('php://output', 'w'); fwrite($o, "\xEF\xBB\xBF");
  fputcsv($o, ['编号', '提交时间', '苗圃', '联系人', '电话/微信', '地址', '总面积(亩)', '品种数', '能供', '类型', '品种', '英文名', '等级', '类别/类群', '种植(亩)', '种植(棵)', '种植明细', '原棵', '分株苗', '鲜切花', '地块', '水淹', '描述/特点', '育种者', '母本', '父本', '杂交年份', '首次开花', '新品种现有植株', '新品种可提供(株)', '照片数', '照片链接']);
  foreach (get_posts(['post_type' => 'pw_supply', 'post_status' => 'private', 'numberposts' => -1]) as $p) {
    $d = pws_get($p->ID); $s = $d['sup'];
    foreach ($d['items'] as $i => $it) {
      $links = []; foreach ($d['photos'] as $k => $aid) if (strpos($k, "i$i-") === 0) $links[] = wp_get_attachment_url($aid);
      $nw = ($it['kind'] ?? '') === 'new'; $of = pws_offers($it);
      fputcsv($o, [$p->ID, get_the_date('Y-m-d H:i', $p), $s['farm'] ?? '', $s['boss'] ?? '', $s['tel'] ?? '', $s['addr'] ?? '', $s['area'] ?? '', $s['vcount'] ?? '', implode('/', (array)($s['types'] ?? [])),
        pws_kind($it), $it['name'] ?? '', $it['en'] ?? '', pws_grade($it), $it['cat'] ?? '', $it['plantMu'] ?? '', $it['plantN'] ?? '', $it['plantText'] ?? '',
        implode('；', $of['原棵']), implode('；', $of['分株苗']), implode('；', $of['鲜切花']), $it['land'] ?? '', $it['flood'] ?? '', $nw ? ($it['note'] ?? '') : ($it['desc'] ?? ''),
        $it['breeder'] ?? '', $it['mom'] ?? '', $it['dad'] ?? '', $it['crossYear'] ?? '', $it['flowerYear'] ?? '', $nw ? pws_newplants($it) : '', $nw ? ($it['offer'] ?? '') : '', count($links), implode(' ', $links)]);
    }
  }
  fclose($o); exit;
});
