<script>
	import { toast } from 'svelte-sonner';

	import { onMount, getContext, tick } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	// [ADDITION]
	let errorMessage = '';

	import { getBackendConfig } from '$lib/apis';
	import { userSignOut } from '$lib/apis/auths';

	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, config, user, socket } from '$lib/stores';

	import { generateInitialsImage, canvasPixelTest } from '$lib/utils';

	import Spinner from '$lib/components/common/Spinner.svelte';
	import OnBoarding from '$lib/components/OnBoarding.svelte';

	const i18n = getContext('i18n');

	let loaded = false;

	async function setLogoImage() {
		await tick();
		const logo = document.getElementById('logo');

		if (logo) {
			const isDarkMode = document.documentElement.classList.contains('dark');

			if (isDarkMode) {
				const darkImage = new Image();
				darkImage.src = '/static/favicon-dark.png';

				darkImage.onload = () => {
					logo.src = '/static/favicon-dark.png';
					logo.style.filter = ''; // Ensure no inversion is applied if favicon-dark.png exists
				};

				darkImage.onerror = () => {
					logo.style.filter = 'invert(1)'; // Invert image if favicon-dark.png is missing
				};
			}
		}
	}

	onMount(async () => {
		
		// [ADDITION]
		// Extract error message from URL parameters
		const urlParams = new URLSearchParams(window.location.search);
		errorMessage = urlParams.get('error') || '';
		
		loaded = true
		return null
	});
</script>

<svelte:head>
	<title>
		{`${$WEBUI_NAME}`}
	</title>
</svelte:head>

<div class="w-full h-screen max-h-[100dvh] relative">
	<div class="w-full h-full absolute top-0 left-0 bg-white dark:bg-black"></div>

	<div class="w-full absolute top-0 left-0 right-0 h-8 drag-region" />

	{#if loaded}
		<div class="fixed m-10 z-50">
			<div class="flex space-x-2">
				<div class=" self-center">
					<img
						id="logo"
						crossorigin="anonymous"
						src="{WEBUI_BASE_URL}/static/favicon.png"
						class=" w-6 rounded-full"
						alt=""
					/>
				</div>
			</div>
		</div>

		<div
			class="absolute w-full h-full backdrop-blur-lg bg-white/10 dark:bg-gray-900/50 flex justify-center"
		>
			<div class="m-auto pb-10 flex flex-col justify-center">
				<div class="max-w-md">
					<div
						class="text-center text-2xl font-medium z-50 text-black dark:text-white"
						style="white-space: pre-wrap;"
					>
						{$i18n.t('Account Not Authorized')}<br />
						<!-- {$i18n.t('Contact Admin for WebUI Access')} -->
					</div>

					<!-- [ADDITION] -->
					{#if errorMessage}
						<div class="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-center">
							<div class="text-sm text-red-700 dark:text-red-300 break-words">
								{errorMessage}
							</div>
						</div>
					{/if}

					<div class="mt-4 text-center text-sm text-gray-700 dark:text-gray-200 w-full">
						<span>{$i18n.t('If you used Globus to sign in, please')}</span>
						<a href="https://auth.globus.org/v2/web/logout" target="_blank" rel="noopener" class="underline text-blue-600 dark:text-blue-400 mx-1">
							{$i18n.t('sign out from Globus')}
						</a>
						<span>{$i18n.t('and sign in again with the correct organization.')}</span>
					</div>

					<div class=" mt-6 mx-auto relative group w-fit">
						<button
							class="relative z-20 flex px-5 py-2 rounded-full bg-white dark:bg-gray-800 border border-gray-100 dark:border-none hover:bg-gray-100 dark:hover:bg-gray-700 text-black dark:text-white transition font-medium text-sm"
							on:click={async () => {
								const res = await userSignOut();
								user.set(null);
								localStorage.removeItem('token');
								location.href = '/auth';
							}}
						>
							{$i18n.t('Return')}
						</button>
					</div>
				</div>
			</div>
		</div>
		<div
			class="fixed bottom-0 left-0 right-0 bg-transparent w-full flex justify-center font-primary text-black dark:text-white p-10"
		>
			<div class="flex space-x-4">
				<div class="bg-white rounded-lg p-2">
					<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 112.9 32.5" class="w-38 h-18">
						<path fill="none" d="M-12.2-13h137.5v54H-12.2z"></path>
						<path fill="#007934" d="M95.9 15.3h-8.1l4 7z"></path>
						<path d="M103.9 15.3h-8.1l-4 7H108l-4.1-7z" fill="#0082ca"></path>
						<path fill="#101e8e" d="M112 15.3h-8.1l4.1 7z"></path>
						<path fill="#fff" d="M103.9 15.3h-8l4-7z"></path>
						<path fill="#a22a2e" d="M103.9 1.3h-8l4 7z"></path>
						<path fill="#d9272e" d="M103.9 1.3l-4 7 4 7h8.1z"></path>
						<path d="M95.9 15.3l4-7-4-7-8.1 14h8.1z" fill="#82bc00"></path>
						<g>
							<path d="M39.3 31l-1.2-2.1c-.2-.3-.3-.6-.5-.9v3h-.8v-4.2h1l1.2 2c.2.3.4.7.5 1v-3h.8V31h-1zM44.2 31l-.3-.9h-1.6l-.2.9h-.8l1.5-4.2h.9l1.5 4.2h-1zm-.9-2.6c-.1-.2-.1-.4-.2-.7 0 .2-.1.5-.2.7l-.4 1.1h1.2l-.4-1.1zM47.4 27.5V31h-.8v-3.5h-1.1v-.7h3v.7h-1.1zM49.4 31v-4.2h.8V31h-.8zM53 31.1c-1.3 0-1.9-.8-1.9-2.1 0-1.4.9-2.2 2-2.2s1.9.7 1.9 2.1c.1 1.3-.8 2.2-2 2.2zm.1-3.6c-.6 0-1.1.5-1.1 1.4 0 .9.3 1.5 1.1 1.5.5 0 1.1-.4 1.1-1.4 0-1-.4-1.5-1.1-1.5zM58.3 31l-1.2-2.1c-.2-.3-.3-.6-.5-.9v3h-.8v-4.2h1l1.2 2c.2.3.4.7.5 1v-3h.8V31h-1zM63.3 31l-.3-.9h-1.6l-.3.9h-.8l1.5-4.2h.9l1.5 4.2h-.9zm-.9-2.6c-.1-.2-.1-.4-.2-.7 0 .2-.1.5-.2.7l-.4 1.1h1.2l-.4-1.1zM65.1 31v-4.2h.8v3.5h1.4v.7h-2.2z"></path>
							<g>
								<path d="M69.8 31v-4.2h.8v3.5H72v.7h-2.2zM75.9 31l-.3-.9H74l-.3.9h-.8l1.5-4.2h.9l1.5 4.2h-.9zm-.9-2.6c-.1-.2-.1-.4-.2-.7 0 .2-.1.5-.2.7l-.4 1.1h1.2l-.4-1.1zM78.9 31h-1.2v-4.2h1.4c.9 0 1.4.4 1.4 1 0 .4-.3.8-.7.9.5.1.7.5.7.9.1.7-.4 1.4-1.6 1.4zm0-3.6h-.5v1.1h.3c.6 0 .8-.2.8-.6.1-.3-.1-.5-.6-.5zm-.1 1.7h-.4v1.2h.4c.5 0 .8-.2.8-.6.1-.4-.3-.6-.8-.6zM83.3 31.1c-1.3 0-1.9-.8-1.9-2.1 0-1.4.9-2.2 2-2.2s1.9.7 1.9 2.1c.1 1.3-.9 2.2-2 2.2zm.1-3.6c-.6 0-1.1.5-1.1 1.4 0 .9.3 1.5 1.1 1.5.5 0 1.1-.4 1.1-1.4 0-1-.4-1.5-1.1-1.5zM88.2 31L87 29.3V31h-.8v-4.2h1.2c.9 0 1.5.3 1.5 1.2 0 .6-.4 1.1-1.1 1.2.1.2.2.3.3.5l1 1.4h-.9zm-.8-3.6h-.3v1.2h.3c.5 0 .8-.3.8-.6-.1-.4-.3-.6-.8-.6zM99.3 31.1c-1.3 0-1.9-.8-1.9-2.1 0-1.4.9-2.2 2-2.2s1.9.7 1.9 2.1c0 1.3-.9 2.2-2 2.2zm0-3.6c-.6 0-1.1.5-1.1 1.4 0 .9.3 1.5 1.1 1.5.5 0 1.1-.4 1.1-1.4 0-1-.4-1.5-1.1-1.5zM104.2 31l-1.2-1.7V31h-.8v-4.2h1.2c.9 0 1.5.3 1.5 1.2 0 .6-.4 1.1-1.1 1.2.1.2.2.3.3.5l1 1.4h-.9zm-.9-3.6h-.3v1.2h.3c.5 0 .8-.3.8-.6-.1-.4-.3-.6-.8-.6zM92.8 31l-.3-.9H91l-.3.9h-.8l1.5-4.2h.9l1.5 4.2h-1zm-.9-2.6c-.1-.2-.1-.4-.2-.7 0 .2-.1.5-.2.7l-.4 1.1h1.2l-.4-1.1zM95.8 27.5V31H95v-3.5h-1.1v-.7h3v.7h-1.1zM107.8 29.5V31h-.8v-1.5l-1.3-2.7h.9l.6 1.2c.1.2.2.5.3.7.1-.2.2-.5.3-.8l.5-1.1h.9l-1.4 2.7z"></path>
							</g>
							<g>
								<path d="M13.4 22.1L11.9 18H4.5L3 22.1H1.1L7.3 5.5h2l6.2 16.6h-2.1zM9 10c-.3-.9-.6-1.6-.8-2.5-.2.8-.5 1.6-.7 2.4L5 16.5h6.3L9 10zM22.9 11.5c-2.7-.4-4 1.6-4 5.7v4.9h-1.8V9.9h1.8c0 .8-.1 2-.3 3.1.5-1.8 1.8-3.6 4.3-3.3v1.8zM28.7 28.5c-3.1 0-5.1-1.3-5.1-3.6 0-1.5 1-2.7 2.1-3.2-.8-.3-1.2-1-1.2-1.8s.5-1.6 1.4-2c-1.2-.7-1.8-2-1.8-3.5 0-2.6 2-4.7 5.3-4.7.5 0 .8 0 1.2.1.2 0 1.8.1 2.1.1h2.7v1.5h-2.3.1c.7.6 1.2 1.5 1.2 2.7 0 2.6-1.8 4.6-5.3 4.6-.6 0-1.2-.1-1.7-.2-.6.2-.9.7-.9 1.1 0 .7.7 1 2.2 1H31c2.7 0 4.1 1.3 4.1 3.4 0 2.6-2.7 4.5-6.4 4.5zm1.8-6.3h-3.3c-1.1.5-1.7 1.4-1.7 2.5 0 1.6 1.5 2.4 3.6 2.4 2.7 0 4.3-1.1 4.3-2.8-.1-1.4-1.1-2.1-2.9-2.1zm-1.3-11.1c-2.1 0-3.4 1.3-3.4 3.1 0 2 1.2 3 3.3 3 2 0 3.3-1.1 3.3-3 0-2-1.2-3.1-3.2-3.1zM41.1 22.3c-3.3 0-5.4-2-5.4-6.3 0-3.5 2.2-6.4 5.8-6.4 3 0 5.4 1.6 5.4 6.1.1 3.7-2.1 6.6-5.8 6.6zm.3-11.1c-1.9 0-3.7 1.5-3.7 4.7 0 3.1 1.4 4.8 3.7 4.8 1.9 0 3.7-1.5 3.7-4.8 0-3-1.3-4.7-3.7-4.7zM56.6 22.1v-7.9c0-1.9-.5-3-2.3-3-2.2 0-3.7 2.2-3.7 5.1v5.9h-1.8V9.9h1.8c0 .8-.1 2-.2 2.7.7-1.8 2.2-3 4.4-3 2.8 0 3.7 1.8 3.7 3.9V22h-1.9zM69.4 22.1v-7.9c0-1.9-.5-3-2.3-3-2.2 0-3.7 2.2-3.7 5.1v5.9h-1.8V9.9h1.8c0 .8-.1 2-.2 2.7.7-1.8 2.2-3 4.4-3 2.8 0 3.7 1.8 3.7 3.9V22h-1.9zM83 15.6h-8.2c-.1 3.7 1.3 5.2 4.1 5.2 1.3 0 2.6-.3 3.5-.8l.2 1.6c-1.1.5-2.5.7-4 .7-3.7 0-5.7-2-5.7-6.3 0-3.7 2-6.4 5.4-6.4 3.4 0 4.8 2.3 4.8 5 0 .3 0 .6-.1 1zM78.2 11c-1.7 0-3 1.3-3.2 3.2h6.2c0-1.9-1.1-3.2-3-3.2z"></path>
							</g>
						</g>
					</svg>
				</div>
				<div class="bg-white rounded-lg p-2 flex">
					<img src="/static/globus.png" alt="Globus" class="size-18" />
				</div>
			</div>
		</div>
	{/if}
</div>
