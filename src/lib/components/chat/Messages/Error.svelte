<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import type { Writable } from 'svelte/store';
	import type { i18n as i18nType } from 'i18next';

	import Info from '$lib/components/icons/Info.svelte';

	const i18n = getContext<Writable<i18nType>>('i18n');
	const dispatch = createEventDispatcher();

	export let content = '';

	const handleClear = () => {
		dispatch('clear');
	};
</script>

<div class="flex my-2 gap-2.5 border px-4 py-3 border-red-600/10 bg-red-600/10 rounded-lg">
	<div class="self-start mt-0.5">
		<Info className="size-5 text-red-700 dark:text-red-400" />
	</div>

	<div class="flex flex-col gap-2 text-sm text-left">
		<div>{typeof content === 'string' ? content : JSON.stringify(content)}</div>
		<button
			type="button"
			class="self-start rounded-md border border-red-500/40 bg-transparent px-3 py-1 text-xs font-medium text-red-700 transition hover:bg-red-500/10 dark:text-red-300"
			on:click={handleClear}
		>
			{$i18n.t('Clear')}
		</button>
	</div>
</div>
